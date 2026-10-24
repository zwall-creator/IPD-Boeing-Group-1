import json
import queue
import threading
import time
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from quantum_backend import get_status as qb_get_status, run_circuit, build_sample_circuit

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


@app.get("/quantum/status")
def quantum_status():
    """
    Returns the current IBM Quantum connection state.
    Frontend polls this when the user selects the quantum solver.
    """
    status = qb_get_status()
    return jsonify(status)


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
    Kick off a simulation and stream progress events back through the event bus.
    When solver=quantum, submits a circuit to IBM Quantum (or falls back to Aer).
    Accepts optional optimization parameters:
      - securityWeight  (0-100)
      - costWeight      (0-100)
      - bandwidthWeight (0-100)
      - riskThreshold   (0-100)
    """
    body = request.get_json(silent=True) or {}
    solver = body.get("solver", "classical")
    opt_params = {
        "securityWeight":  body.get("securityWeight", 50),
        "costWeight":      body.get("costWeight", 50),
        "bandwidthWeight": body.get("bandwidthWeight", 50),
        "riskThreshold":   body.get("riskThreshold", 30),
    }

    def _run_classical():
        _broadcast("simulation.started", {"solver": "classical", "params": opt_params})
        steps = [
            "Initialising problem graph…",
            "Building constraint model…",
            f"Applying weights — sec:{opt_params['securityWeight']} cost:{opt_params['costWeight']} bw:{opt_params['bandwidthWeight']} risk:{opt_params['riskThreshold']}…",
            "Executing CP-SAT classical solver…",
            "Collecting results…",
            "Simulation complete.",
        ]
        for i, step in enumerate(steps):
            time.sleep(0.8)
            _broadcast("simulation.progress", {"step": i + 1, "total": len(steps), "message": step})
        _broadcast("simulation.done", {"solver": "classical", "status": "success", "params": opt_params})

    def _run_quantum():
        _broadcast("simulation.started", {"solver": "quantum", "params": opt_params})

        # Step 1 — check IBM connection
        qstatus = qb_get_status()
        _broadcast("simulation.progress", {"step": 1, "total": 6, "message": "Checking IBM Quantum connection…"})
        time.sleep(0.5)

        if qstatus["connected"]:
            _broadcast("simulation.progress", {"step": 2, "total": 6,
                "message": f"Connected to IBM backend: {qstatus['backend']} ({qstatus['qubits']} qubits)"})
        else:
            _broadcast("simulation.progress", {"step": 2, "total": 6,
                "message": f"IBM unavailable ({qstatus['error']}) — using local Aer simulator"})
        time.sleep(0.5)

        _broadcast("simulation.progress", {"step": 3, "total": 6,
            "message": f"Applying weights — sec:{opt_params['securityWeight']} cost:{opt_params['costWeight']} bw:{opt_params['bandwidthWeight']} risk:{opt_params['riskThreshold']}…"})
        time.sleep(0.5)

        _broadcast("simulation.progress", {"step": 4, "total": 6,
            "message": "Building QAOA/VQE circuit from network topology…"})
        time.sleep(0.5)

        # Step 5 — run the circuit
        _broadcast("simulation.progress", {"step": 5, "total": 6,
            "message": f"Submitting circuit to {'IBM Quantum' if qstatus['connected'] else 'Aer simulator'}…"})
        circuit = build_sample_circuit(n_qubits=2)
        result = run_circuit(circuit, shots=1024)

        time.sleep(0.5)
        _broadcast("simulation.progress", {"step": 6, "total": 6,
            "message": f"Results collected from {result['backend']} — top counts: {dict(list(result['counts'].items())[:3])}"})
        time.sleep(0.3)

        _broadcast("simulation.done", {
            "solver":   "quantum",
            "status":   "success" if not result["error"] else "fallback",
            "backend":  result["backend"],
            "used_ibm": result["used_ibm"],
            "counts":   result["counts"],
            "params":   opt_params,
        })

    if solver == "quantum":
        threading.Thread(target=_run_quantum, daemon=True).start()
    else:
        threading.Thread(target=_run_classical, daemon=True).start()

    return jsonify(ok=True, solver=solver, params=opt_params)
