import json
import queue
import threading
import time
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from quantum_backend import get_status as qb_get_status, run_circuit, build_sample_circuit
from network_problem import build_problem_from_dicts, build_toy_problem
from qaoa_solver import solve_qaoa
from classical_solver import solve_exhaustive, solve_greedy, compare_results
from result_validator import validate_placement, format_validation_report
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
    # Capture topology from request body (may be empty — solvers fall back to toy network)
    req_nodes = body.get("nodes", [])
    req_edges = body.get("edges", [])

    def _run_classical():
        run_id = db.insert_run("classical", opt_params)
        _broadcast("simulation.started", {"solver": "classical", "params": opt_params, "run_id": run_id})

        # Step 1 — build the problem
        msg = "Building network optimisation problem…"
        _broadcast("simulation.progress", {"step": 1, "total": 7, "message": msg})
        db.insert_log(run_id, 1, 7, msg)
        time.sleep(0.3)

        nodes = req_nodes
        edges = req_edges
        if not nodes:
            problem = build_toy_problem(opt_params)
            msg = f"No topology provided — using toy network ({problem.n} nodes, {len(problem.edges)} edges)"
        else:
            problem = build_problem_from_dicts(nodes, edges, opt_params)
            msg = f"Topology loaded: {problem.n} nodes, {len(problem.edges)} edges"
        _broadcast("simulation.progress", {"step": 2, "total": 7, "message": msg})
        db.insert_log(run_id, 2, 7, msg)
        time.sleep(0.3)

        # Step 3 — build QUBO
        msg = (f"QUBO matrix built ({problem.n}×{problem.n}) — "
               f"sec:{opt_params['securityWeight']} cost:{opt_params['costWeight']} "
               f"bw:{opt_params['bandwidthWeight']} risk:{opt_params['riskThreshold']}")
        _broadcast("simulation.progress", {"step": 3, "total": 7, "message": msg})
        db.insert_log(run_id, 3, 7, msg)
        time.sleep(0.3)

        # Step 4 — run classical solver
        msg = "Running exhaustive classical solver…"
        _broadcast("simulation.progress", {"step": 4, "total": 7, "message": msg})
        db.insert_log(run_id, 4, 7, msg)
        classical_result = solve_exhaustive(problem)
        time.sleep(0.3)

        placement_str = ''.join(str(x) for x in classical_result["placement"])
        msg = (f"Classical solver done — placement: {placement_str} | "
               f"QUBO cost: {classical_result['qubo_cost']:.4f} | "
               f"strategy: {classical_result['strategy']}")
        _broadcast("simulation.progress", {"step": 5, "total": 7, "message": msg})
        db.insert_log(run_id, 5, 7, msg)
        time.sleep(0.3)

        # Step 6 — validate
        validation = validate_placement(problem, classical_result["placement"])
        report = format_validation_report(validation, classical_result["placement"])
        for line in report.split("\n"):
            _broadcast("simulation.progress", {"step": 6, "total": 7, "message": line})
            db.insert_log(run_id, 6, 7, line)
        time.sleep(0.3)

        # Step 7 — done
        status = "success" if validation["valid"] else "invalid"
        msg = f"Classical simulation complete — result: {status.upper()}"
        _broadcast("simulation.progress", {"step": 7, "total": 7, "message": msg})
        db.insert_log(run_id, 7, 7, msg)

        db.insert_result(run_id, {
            "backend":      "classical_exhaustive",
            "used_ibm":     False,
            "shots":        None,
            "counts":       {"placement": placement_str},
            "execution_ms": None,
        })
        db.update_run_status(run_id, status)
        _broadcast("simulation.done", {
            "solver":     "classical",
            "status":     status,
            "placement":  classical_result["placement"],
            "qubo_cost":  classical_result["qubo_cost"],
            "valid":      validation["valid"],
            "violations": validation["violations"],
            "warnings":   validation["warnings"],
            "params":     opt_params,
            "run_id":     run_id,
        })

    def _run_quantum():
        run_id = db.insert_run("quantum", opt_params)
        _broadcast("simulation.started", {"solver": "quantum", "params": opt_params, "run_id": run_id})

        # Step 1 — IBM connection check
        qstatus = qb_get_status()
        if qstatus["connected"]:
            msg1 = f"IBM Quantum connected — backend: {qstatus['backend']} ({qstatus['qubits']} qubits)"
        else:
            msg1 = f"IBM unavailable ({qstatus['error']}) — using local Aer simulator"
        _broadcast("simulation.progress", {"step": 1, "total": 9, "message": msg1})
        db.insert_log(run_id, 1, 9, msg1)
        time.sleep(0.3)

        # Step 2 — build problem
        nodes = req_nodes
        edges = req_edges
        if not nodes:
            problem = build_toy_problem(opt_params)
            msg2 = f"No topology provided — using toy network ({problem.n} nodes, {len(problem.edges)} edges)"
        else:
            problem = build_problem_from_dicts(nodes, edges, opt_params)
            msg2 = f"Topology loaded: {problem.n} nodes, {len(problem.edges)} edges"
        _broadcast("simulation.progress", {"step": 2, "total": 9, "message": msg2})
        db.insert_log(run_id, 2, 9, msg2)
        time.sleep(0.3)

        # Step 3 — QUBO
        msg3 = (f"QUBO encoded ({problem.n} qubits) — "
                f"sec:{opt_params['securityWeight']} cost:{opt_params['costWeight']} "
                f"bw:{opt_params['bandwidthWeight']} risk:{opt_params['riskThreshold']}")
        _broadcast("simulation.progress", {"step": 3, "total": 9, "message": msg3})
        db.insert_log(run_id, 3, 9, msg3)
        time.sleep(0.3)

        # Step 4 — classical baseline (for comparison)
        msg4 = "Computing classical baseline (exhaustive solver)…"
        _broadcast("simulation.progress", {"step": 4, "total": 9, "message": msg4})
        db.insert_log(run_id, 4, 9, msg4)
        classical_result = solve_exhaustive(problem)
        time.sleep(0.3)

        # Step 5 — build & describe QAOA circuit
        from qaoa_solver import build_qaoa_circuit
        circuit = build_qaoa_circuit(problem, gamma=0.4, beta=0.3, p=1)
        msg5 = (f"QAOA circuit built — depth: {circuit.depth()}, "
                f"qubits: {circuit.num_qubits}, layers: p=1")
        _broadcast("simulation.progress", {"step": 5, "total": 9, "message": msg5})
        db.insert_log(run_id, 5, 9, msg5)
        time.sleep(0.3)

        # Step 6 — run QAOA
        backend_label = "IBM Quantum" if qstatus["connected"] else "Aer simulator"
        msg6 = f"Submitting QAOA circuit to {backend_label} (1024 shots)…"
        _broadcast("simulation.progress", {"step": 6, "total": 9, "message": msg6})
        db.insert_log(run_id, 6, 9, msg6)

        quantum_result = solve_qaoa(problem, shots=1024)
        time.sleep(0.3)

        placement_str = ''.join(str(x) for x in quantum_result["placement"])
        msg7 = (f"QAOA result — placement: {placement_str} | "
                f"confidence: {quantum_result['confidence']:.1%} | "
                f"QUBO cost: {quantum_result['qubo_cost']:.4f} | "
                f"backend: {quantum_result['backend']}")
        _broadcast("simulation.progress", {"step": 7, "total": 9, "message": msg7})
        db.insert_log(run_id, 7, 9, msg7)
        time.sleep(0.3)

        # Step 8 — compare vs classical
        comparison = compare_results(quantum_result, classical_result)
        msg8 = (f"Comparison vs classical — {comparison['verdict']} | "
                f"quantum cost: {comparison['quantum_cost']:.4f} | "
                f"classical cost: {comparison['classical_cost']:.4f} | "
                f"gap: {comparison['relative_gap']:.1%}")
        _broadcast("simulation.progress", {"step": 8, "total": 9, "message": msg8})
        db.insert_log(run_id, 8, 9, msg8)
        time.sleep(0.3)

        # Step 9 — validate
        validation = validate_placement(problem, quantum_result["placement"])
        report = format_validation_report(validation, quantum_result["placement"])
        for line in report.split("\n"):
            _broadcast("simulation.progress", {"step": 9, "total": 9, "message": line})
            db.insert_log(run_id, 9, 9, line)

        final_status = "success" if validation["valid"] else "invalid"
        if quantum_result.get("error") and not quantum_result.get("used_ibm"):
            final_status = "fallback"

        db.insert_result(run_id, {
            "backend":      quantum_result["backend"],
            "used_ibm":     quantum_result["used_ibm"],
            "shots":        1024,
            "counts":       quantum_result.get("all_counts", {}),
            "execution_ms": None,
        })
        db.update_run_status(run_id, final_status, quantum_result.get("error"))

        _broadcast("simulation.done", {
            "solver":           "quantum",
            "status":           final_status,
            "placement":        quantum_result["placement"],
            "qubo_cost":        quantum_result["qubo_cost"],
            "confidence":       quantum_result["confidence"],
            "backend":          quantum_result["backend"],
            "used_ibm":         quantum_result["used_ibm"],
            "classical_match":  comparison["match"],
            "comparison":       comparison,
            "valid":            validation["valid"],
            "violations":       validation["violations"],
            "warnings":         validation["warnings"],
            "params":           opt_params,
            "run_id":           run_id,
        })

    if solver == "quantum":
        threading.Thread(target=_run_quantum, daemon=True).start()
    else:
        threading.Thread(target=_run_classical, daemon=True).start()

    return jsonify(ok=True, solver=solver, params=opt_params)
