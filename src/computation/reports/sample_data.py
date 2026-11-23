"""
Used Claude Opus 5.5 to help write this code.

reports/sample_data.py
----------------------
SAMPLE (FAKE) benchmark data for the report generation service.

Not every solver backend runs end to end yet, so this module produces
benchmark records that have the same shape real runs will have. Everything
downstream (builder.py, pdf_renderer.py, the Reports page) only depends on
that shape, so swapping in real data later means writing one new
function that returns the same structure from the database. Nothing else
needs to change.

Record shape (one per solver x scenario x trial):
    {
        "solver_id":       "cpsat" | "bruteforce" | "greedy" | "qaoa_aer",
        "scenario_id":     str,
        "trial":           int,
        "status":          "optimal" | "feasible" | "infeasible" | "timeout" | "skipped",
        "runtime_ms":      float | None,
        "objective":       float | None,   # total security gap, lower is better
        "devices_placed":  int | None,
        "nodes_protected": int | None,
        "violations":      int,
        "extra":           dict,           # solver-specific (qubits, depth, shots...)
        "note":            str | None,     # why a run was skipped / timed out
    }

The numbers are generated from a seeded RNG, so a given seed always gives
the same report. The trends are made up to look plausible (exact solvers
scale badly, greedy is fast but suboptimal, QAOA is limited by qubit count);
they are not measured results.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Static catalogue: solvers and scenarios
# ---------------------------------------------------------------------------

SOLVERS = [
    {
        "id": "cpsat",
        "name": "CP-SAT",
        "paradigm": "Classical (exact)",
        "description": "OR-Tools constraint programming / SAT solver over the link-placement model.",
    },
    {
        "id": "bruteforce",
        "name": "Brute Force",
        "paradigm": "Classical (exact)",
        "description": "Enumerates every device-to-link assignment. Ground truth for small networks.",
    },
    {
        "id": "greedy",
        "name": "Greedy",
        "paradigm": "Classical (heuristic)",
        "description": "Places each device on the link with the largest immediate security gain.",
    },
    {
        "id": "qaoa_aer",
        "name": "QAOA (Aer)",
        "paradigm": "Quantum (simulated)",
        "description": "QUBO formulation solved with QAOA (p=1) on the local Qiskit Aer simulator.",
    },
]

# nodes / links / devices. The first three match the frontend layout presets.
SCENARIOS = [
    {"id": "lan",        "name": "Office LAN",  "nodes": 5,  "links": 4,  "devices": 2},
    {"id": "dmz",        "name": "DMZ",         "nodes": 4,  "links": 3,  "devices": 2},
    {"id": "wan",        "name": "Branch WAN",  "nodes": 5,  "links": 4,  "devices": 2},
    {"id": "campus",     "name": "Campus",      "nodes": 12, "links": 16, "devices": 3},
    {"id": "enterprise", "name": "Enterprise",  "nodes": 24, "links": 36, "devices": 4},
    {"id": "datacenter", "name": "Datacenter",  "nodes": 48, "links": 80, "devices": 6},
]

# Limits used by the fake runs (and shown in the report config)
DEFAULT_TIME_LIMIT_S = 60
AER_MAX_QUBITS = 28


def _decision_vars(scenario: dict) -> int:
    """x[device, link] binaries, which is also the QAOA qubit count."""
    return scenario["links"] * scenario["devices"]


# ---------------------------------------------------------------------------
# Per-solver fake behaviour
# ---------------------------------------------------------------------------

def _jitter(rng: random.Random, value: float, pct: float = 0.12) -> float:
    return max(0.01, value * rng.gauss(1.0, pct))


def _fake_trial(rng, solver_id, scenario, optimum, time_limit_ms):
    n_vars = _decision_vars(scenario)
    nodes = scenario["nodes"]
    devices = scenario["devices"]
    base = {
        "devices_placed": devices,
        "violations": 0,
        "extra": {"decision_vars": n_vars},
        "note": None,
    }

    if solver_id == "cpsat":
        runtime = _jitter(rng, 4.0 + 0.05 * n_vars ** 1.7)
        if n_vars > 300:
            # Big model: stopped at the time limit with a good but unproven solution
            return {**base, "status": "feasible", "runtime_ms": time_limit_ms * rng.uniform(0.2, 0.35),
                    "objective": optimum * rng.uniform(1.01, 1.03),
                    "nodes_protected": nodes - rng.randint(1, 2)}
        return {**base, "status": "optimal", "runtime_ms": runtime, "objective": optimum,
                "nodes_protected": nodes - (1 if nodes > 8 else 0)}

    if solver_id == "bruteforce":
        runtime = 0.0008 * (2 ** n_vars)
        if runtime > time_limit_ms:
            return {**base, "status": "timeout", "runtime_ms": None, "objective": None,
                    "devices_placed": None, "nodes_protected": None,
                    "note": f"2^{n_vars} assignments; exceeds {time_limit_ms / 1000:.0f} s limit"}
        return {**base, "status": "optimal", "runtime_ms": _jitter(rng, runtime + 0.3, 0.05),
                "objective": optimum, "nodes_protected": nodes}

    if solver_id == "greedy":
        runtime = _jitter(rng, 0.15 + 0.004 * n_vars * math.log2(n_vars + 1))
        quality = 1.0 + abs(rng.gauss(0.04 + 0.002 * n_vars ** 0.8, 0.03))
        return {**base, "status": "feasible", "runtime_ms": runtime,
                "objective": optimum * quality,
                "nodes_protected": max(1, nodes - rng.randint(1, max(1, nodes // 4)))}

    if solver_id == "qaoa_aer":
        if n_vars > AER_MAX_QUBITS:
            return {**base, "status": "skipped", "runtime_ms": None, "objective": None,
                    "devices_placed": None, "nodes_protected": None,
                    "extra": {"qubits": n_vars},
                    "note": f"needs {n_vars} qubits; Aer limit set to {AER_MAX_QUBITS}"}
        depth = 6 + 4 * n_vars
        runtime = _jitter(rng, 350 + 45 * n_vars + 2 ** (n_vars / 2.2), 0.08)
        extra = {"qubits": n_vars, "circuit_depth": depth, "shots": 1024,
                 "confidence": round(rng.uniform(0.18, 0.62), 3)}
        if rng.random() < 0.15 + 0.01 * n_vars:
            # Most likely bitstring broke a one-device-per-link constraint
            return {**base, "status": "infeasible", "runtime_ms": runtime, "objective": None,
                    "devices_placed": devices + rng.choice([-1, 1]), "nodes_protected": None,
                    "violations": rng.randint(1, 2), "extra": extra,
                    "note": "measured bitstring violates placement constraints"}
        quality = 1.0 + abs(rng.gauss(0.0, 0.07))
        return {**base, "status": "feasible" if quality > 1.0005 else "optimal",
                "runtime_ms": runtime, "objective": optimum * quality,
                "nodes_protected": nodes - rng.randint(0, 1), "extra": extra}

    raise ValueError(f"unknown solver {solver_id}")


def generate_records(seed: int, scenario_ids=None, trials: int = 5,
                     time_limit_s: int = DEFAULT_TIME_LIMIT_S) -> list[dict]:
    """Produce fake benchmark records for every solver x scenario x trial."""
    rng = random.Random(seed)
    scenarios = [s for s in SCENARIOS if scenario_ids is None or s["id"] in scenario_ids]
    records = []
    for scenario in scenarios:
        # "True" optimum of the total security gap for this scenario
        optimum = round(scenario["nodes"] * rng.uniform(1.4, 2.6), 2)
        for solver in SOLVERS:
            for t in range(trials):
                rec = _fake_trial(rng, solver["id"], scenario, optimum, time_limit_s * 1000)
                records.append({"solver_id": solver["id"], "scenario_id": scenario["id"],
                                "trial": t + 1, **rec})
    return records


# ---------------------------------------------------------------------------
# Sample report catalogue (what GET /reports lists)
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 11, 20, 15, 0, tzinfo=timezone.utc)

SAMPLE_REPORTS = [
    {
        "id": "sample-001",
        "title": "Baseline benchmark: balanced weights",
        "seed": 11,
        "scenario_ids": None,
        "trials": 5,
        "opt_params": {"securityWeight": 50, "costWeight": 50, "bandwidthWeight": 50, "riskThreshold": 30},
        "generated_at": _NOW.isoformat(),
    },
    {
        "id": "sample-002",
        "title": "Security-priority weighting",
        "seed": 27,
        "scenario_ids": None,
        "trials": 5,
        "opt_params": {"securityWeight": 85, "costWeight": 30, "bandwidthWeight": 40, "riskThreshold": 20},
        "generated_at": (_NOW - timedelta(days=2, hours=3)).isoformat(),
    },
    {
        "id": "sample-003",
        "title": "Small networks: all solvers head to head",
        "seed": 42,
        "scenario_ids": ["lan", "dmz", "wan"],
        "trials": 20,
        "opt_params": {"securityWeight": 50, "costWeight": 50, "bandwidthWeight": 50, "riskThreshold": 30},
        "generated_at": (_NOW - timedelta(days=5)).isoformat(),
    },
]
