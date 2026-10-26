import json
import queue
import threading
import time
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from quantum_backend import get_status as qb_get_status, run_circuit, build_sample_circuit
import db

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


@app.get("/runs")
def get_runs():
    """Return the 20 most recent simulation runs with their results."""
    runs = db.get_runs(limit=20)
    # Convert datetime objects to ISO strings for JSON serialisation
    for run in runs:
        for key in ("started_at", "completed_at"):
            if run.get(key) is not None:
                run[key] = run[key].isoformat()
    return jsonify(runs)


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
        run_id = db.insert_run("classical", opt_params)
        _broadcast("simulation.started", {"solver": "classical", "params": opt_params, "run_id": run_id})
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
            db.insert_log(run_id, i + 1, len(steps), step)
        db.update_run_status(run_id, "success")
        _broadcast("simulation.done", {"solver": "classical", "status": "success", "params": opt_params, "run_id": run_id})

    def _run_quantum():
        run_id = db.insert_run("quantum", opt_params)
        _broadcast("simulation.started", {"solver": "quantum", "params": opt_params, "run_id": run_id})

        # Step 1 — check IBM connection
        qstatus = qb_get_status()
        msg1 = "Checking IBM Quantum connection…"
        _broadcast("simulation.progress", {"step": 1, "total": 6, "message": msg1})
        db.insert_log(run_id, 1, 6, msg1)
        time.sleep(0.5)

        if qstatus["connected"]:
            msg2 = f"Connected to IBM backend: {qstatus['backend']} ({qstatus['qubits']} qubits)"
        else:
            msg2 = f"IBM unavailable ({qstatus['error']}) — using local Aer simulator"
        _broadcast("simulation.progress", {"step": 2, "total": 6, "message": msg2})
        db.insert_log(run_id, 2, 6, msg2)
        time.sleep(0.5)

        msg3 = f"Applying weights — sec:{opt_params['securityWeight']} cost:{opt_params['costWeight']} bw:{opt_params['bandwidthWeight']} risk:{opt_params['riskThreshold']}…"
        _broadcast("simulation.progress", {"step": 3, "total": 6, "message": msg3})
        db.insert_log(run_id, 3, 6, msg3)
        time.sleep(0.5)

        msg4 = "Building QAOA/VQE circuit from network topology…"
        _broadcast("simulation.progress", {"step": 4, "total": 6, "message": msg4})
        db.insert_log(run_id, 4, 6, msg4)
        time.sleep(0.5)

        # Step 5 — run the circuit
        msg5 = f"Submitting circuit to {'IBM Quantum' if qstatus['connected'] else 'Aer simulator'}…"
        _broadcast("simulation.progress", {"step": 5, "total": 6, "message": msg5})
        db.insert_log(run_id, 5, 6, msg5)
        circuit = build_sample_circuit(n_qubits=2)
        result = run_circuit(circuit, shots=1024)
        time.sleep(0.5)

        msg6 = f"Results collected from {result['backend']} — top counts: {dict(list(result['counts'].items())[:3])}"
        _broadcast("simulation.progress", {"step": 6, "total": 6, "message": msg6})
        db.insert_log(run_id, 6, 6, msg6)
        time.sleep(0.3)

        final_status = "success" if not result.get("error") or result["used_ibm"] else "fallback"
        db.insert_result(run_id, result)
        db.update_run_status(run_id, final_status, result.get("error"))

        _broadcast("simulation.done", {
            "solver":   "quantum",
            "status":   final_status,
            "backend":  result["backend"],
            "used_ibm": result["used_ibm"],
            "counts":   result["counts"],
            "params":   opt_params,
            "run_id":   run_id,
        })

    if solver == "quantum":
        threading.Thread(target=_run_quantum, daemon=True).start()
    else:
        threading.Thread(target=_run_classical, daemon=True).start()

    return jsonify(ok=True, solver=solver, params=opt_params)
