"""
Used Claude Opus 5.5 to help write this code.

reports/builder.py
------------------
Turns raw benchmark records into a solver comparison report.

This module does not care where records come from (sample_data.py today,
the database later). It aggregates trials into one result per
solver x scenario, scores each result against the best known objective for
that scenario, and rolls everything up per solver.

Report shape returned by build_report(): see the README in this folder.
"""

from __future__ import annotations

import statistics
from collections import defaultdict

SOLVED = {"optimal", "feasible"}       # statuses that produced a usable placement
OPTIMAL_TOL_PCT = 0.01                 # gap below this counts as matching the best known


def _mean(xs):
    return statistics.fmean(xs) if xs else None


def _std(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _aggregate_cell(trials: list[dict]) -> dict:
    """Collapse the trials of one solver on one scenario into a single result."""
    solved = [t for t in trials if t["status"] in SOLVED]
    runtimes = [t["runtime_ms"] for t in trials if t["runtime_ms"] is not None]
    objectives = [t["objective"] for t in solved if t["objective"] is not None]

    statuses = [t["status"] for t in trials]
    if not solved:
        # Everything failed the same way? Report that status (timeout / skipped / infeasible).
        status = max(set(statuses), key=statuses.count)
    elif all(s == "optimal" for s in statuses):
        status = "optimal"
    else:
        status = "feasible"

    extras = [t.get("extra") or {} for t in trials]
    extra = {}
    for key in ("qubits", "circuit_depth", "shots", "decision_vars"):
        vals = [e[key] for e in extras if key in e]
        if vals:
            extra[key] = vals[0]
    conf = [e["confidence"] for e in extras if "confidence" in e]
    if conf:
        extra["confidence_mean"] = round(_mean(conf), 3)

    notes = [t["note"] for t in trials if t.get("note")]
    return {
        "status": status,
        "trials": len(trials),
        "success_rate": len(solved) / len(trials) if trials else 0.0,
        "runtime_ms_mean": _mean(runtimes),
        "runtime_ms_std": _std(runtimes) if runtimes else None,
        "objective_mean": _mean(objectives),
        "objective_best": min(objectives) if objectives else None,
        "nodes_protected_mean": _mean([t["nodes_protected"] for t in solved if t["nodes_protected"] is not None]),
        "violations_total": sum(t.get("violations", 0) for t in trials),
        "extra": extra,
        "note": notes[0] if notes else None,
    }


def build_report(meta: dict, solvers: list[dict], scenarios: list[dict], records: list[dict]) -> dict:
    """
    meta     : id, title, generated_at, is_sample_data, config (trials, time_limit_s, opt_params)
    solvers  : [{id, name, paradigm, description}]
    scenarios: [{id, name, nodes, links, devices}]
    records  : raw per-trial records (see sample_data.py for the shape)
    """
    used_scenarios = {r["scenario_id"] for r in records}
    scenarios = [s for s in scenarios if s["id"] in used_scenarios]
    scenarios.sort(key=lambda s: (s["nodes"] * s["links"], s["name"]))

    grouped = defaultdict(list)
    for r in records:
        grouped[(r["solver_id"], r["scenario_id"])].append(r)

    # 1. One result per solver x scenario
    results = []
    for sc in scenarios:
        for sv in solvers:
            trials = grouped.get((sv["id"], sc["id"]))
            if trials:
                results.append({"solver_id": sv["id"], "scenario_id": sc["id"], **_aggregate_cell(trials)})

    # 2. Best known objective per scenario, then optimality gap for each result
    best_known = {}
    for sc in scenarios:
        objs = [r["objective_best"] for r in results
                if r["scenario_id"] == sc["id"] and r["objective_best"] is not None]
        best_known[sc["id"]] = min(objs) if objs else None
    for r in results:
        best = best_known[r["scenario_id"]]
        if r["objective_mean"] is None or best is None:
            r["optimality_gap_pct"] = None
        else:
            r["optimality_gap_pct"] = round(100 * (r["objective_mean"] - best) / max(best, 1e-9), 3)
    for sc in scenarios:
        sc["best_known_objective"] = best_known[sc["id"]]

    # 3. Roll up per solver
    summary = []
    for sv in solvers:
        rows = [r for r in results if r["solver_id"] == sv["id"]]
        solved = [r for r in rows if r["status"] in SOLVED]
        # skipped = never attempted (e.g. too many qubits), so it doesn't count against success
        ran = [r for r in rows if r["status"] != "skipped"]
        total_trials = sum(r["trials"] for r in ran)
        ok_trials = sum(r["success_rate"] * r["trials"] for r in ran)
        gaps = [r["optimality_gap_pct"] for r in solved if r["optimality_gap_pct"] is not None]
        largest = max(solved, key=lambda r: next(s["nodes"] for s in scenarios if s["id"] == r["scenario_id"]),
                      default=None)
        summary.append({
            "solver_id": sv["id"],
            "scenarios_attempted": len(rows),
            "scenarios_solved": len(solved),
            "success_rate": ok_trials / total_trials if total_trials else 0.0,
            "runtime_ms_mean": _mean([r["runtime_ms_mean"] for r in solved if r["runtime_ms_mean"] is not None]),
            "optimality_gap_pct_mean": _mean(gaps),
            "matched_best_count": sum(1 for g in gaps if g <= OPTIMAL_TOL_PCT),
            "largest_solved_scenario": largest["scenario_id"] if largest else None,
        })

    return {
        **meta,
        "solvers": solvers,
        "scenarios": scenarios,
        "results": results,
        "summary": summary,
    }
