import json
import queue
import threading
import time
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Event bus — a simple thread-safe broadcast queue.
# Each subscriber gets their own Queue. When an event is emitted, it is placed
# into every subscriber's queue so all open SSE connections receive it.
# ---------------------------------------------------------------------------

_subscribers: list[queue.Queue] = []
_subscribers_lock = threading.Lock()


def _subscribe() -> queue.Queue:
    """Register a new SSE client and return its dedicated queue."""
    q: queue.Queue = queue.Queue(maxsize=100)
    with _subscribers_lock:
        _subscribers.append(q)
    return q


def _unsubscribe(q: queue.Queue) -> None:
    """Remove a disconnected client's queue."""
    with _subscribers_lock:
        try:
            _subscribers.remove(q)
        except ValueError:
            pass


def _broadcast(event_type: str, data: dict) -> None:
    """Push an event to every connected SSE client."""
    payload = json.dumps({"type": event_type, "data": data, "timestamp": time.time()})
    with _subscribers_lock:
        dead: list[queue.Queue] = []
        for q in _subscribers:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify(status="ok", subscribers=len(_subscribers))


@app.get("/events/stream")
def stream():
    """
    SSE endpoint.  Clients open one long-lived GET connection here and receive
    newline-delimited `data: ...\n\n` frames whenever an event is broadcast.
    """
    q = _subscribe()

    def generate():
        # Send an immediate connected acknowledgement
        yield f"data: {json.dumps({'type': 'connected', 'data': {}, 'timestamp': time.time()})}\n\n"
        try:
            while True:
                try:
                    # Block for up to 25 s, then send a keep-alive comment so
                    # the browser doesn't time-out the connection.
                    payload = q.get(timeout=25)
                    yield f"data: {payload}\n\n"
                except queue.Empty:
                    # SSE comment — ignored by EventSource, keeps TCP alive
                    yield ": keep-alive\n\n"
        except GeneratorExit:
            pass
        finally:
            _unsubscribe(q)

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",   # disable nginx buffering if behind a proxy
    }
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers=headers,
    )


@app.post("/events/emit")
def emit():
    """
    POST { "type": "...", "data": { ... } }
    Broadcasts an event to every connected SSE client.
    Useful for the frontend to trigger server-side notifications, or for
    backend computation tasks to push progress updates.
    """
    body = request.get_json(silent=True) or {}
    event_type = body.get("type", "message")
    data = body.get("data", {})

    _broadcast(event_type, data)
    return jsonify(ok=True, type=event_type, subscribers=len(_subscribers))


@app.post("/simulation/run")
def run_simulation():
    """
    Kick off a mock simulation and stream progress events back through the
    event bus so every connected client sees them in real time.
    """
    body = request.get_json(silent=True) or {}
    solver = body.get("solver", "classical")

    def _run():
        _broadcast("simulation.started", {"solver": solver})
        steps = [
            "Initialising problem graph…",
            "Building constraint model…",
            f"Executing {'CP-SAT classical solver' if solver == 'classical' else 'QAOA/VQE quantum circuit'}…",
            "Collecting results…",
            "Simulation complete.",
        ]
        for i, step in enumerate(steps):
            time.sleep(0.8)
            _broadcast("simulation.progress", {"step": i + 1, "total": len(steps), "message": step})
        _broadcast("simulation.done", {"solver": solver, "status": "success"})

    threading.Thread(target=_run, daemon=True).start()
    return jsonify(ok=True, solver=solver)
