"""
classical_solver.py
-------------------
Classical baseline solver for the network placement QUBO.

Two strategies are provided:

1. Greedy solver  — O(N) deterministic baseline.
   For each node in descending security-deficit order, deploy a resource
   if the expected benefit (security gain) exceeds the cost.
   Always produces a valid feasible solution.

2. Exhaustive solver — O(2^N) exact solver for small N (N ≤ 20).
   Enumerates all 2^N binary assignments and returns the one with the
   lowest QUBO objective value.  Used as the ground-truth reference
   for validating the quantum result on toy networks.

The exhaustive solver is the 'classical answer' that the acceptance
criteria requires the quantum solver to match on the toy network.
"""

from __future__ import annotations
import itertools
import logging
from network_problem import NetworkProblem
from qaoa_solver import evaluate_qubo

log = logging.getLogger(__name__)

# Maximum problem size for the exhaustive solver (2^20 = ~1M combinations)
EXHAUSTIVE_MAX_N = 20


# ---------------------------------------------------------------------------
# Greedy solver
# ---------------------------------------------------------------------------

def solve_greedy(problem: NetworkProblem) -> dict:
    """
    Greedy node-placement solver.

    Strategy: rank nodes by security deficit (risk_level - base_sec_level).
    Deploy resources to nodes with the largest deficits first, stopping
    when additional deployments no longer improve the objective.

    Returns
    -------
    dict with keys:
        placement   — list[int]
        qubo_cost   — float
        strategy    — "greedy"
        valid       — bool (always True for greedy)
    """
    n = problem.n
    Q = problem.Q

    # Score each node: higher deficit = higher priority
    scores = []
    for i, node in enumerate(problem.nodes):
        deficit = node.risk_level - node.base_sec_level
        scores.append((deficit, i))
    scores.sort(reverse=True)

    placement = [0] * n
    current_cost = evaluate_qubo(placement, Q)

    for _, i in scores:
        # Try deploying to node i
        trial = placement[:]
        trial[i] = 1
        trial_cost = evaluate_qubo(trial, Q)
        if trial_cost < current_cost:
            placement = trial
            current_cost = trial_cost

    return {
        "placement": placement,
        "qubo_cost": current_cost,
        "strategy":  "greedy",
        "valid":     True,
    }


# ---------------------------------------------------------------------------
# Exhaustive solver
# ---------------------------------------------------------------------------

def solve_exhaustive(problem: NetworkProblem) -> dict:
    """
    Exhaustive (exact) solver. Enumerates all 2^N placements and returns
    the globally optimal one.

    Only suitable for small problems (N ≤ 20).

    Returns
    -------
    dict with keys:
        placement     — list[int] (optimal)
        qubo_cost     — float (minimum QUBO value)
        strategy      — "exhaustive"
        valid         — bool
        n_evaluated   — int (number of placements checked)
    """
    n = problem.n
    Q = problem.Q

    if n > EXHAUSTIVE_MAX_N:
        log.warning(
            "Problem size N=%d exceeds exhaustive solver limit (%d). "
            "Falling back to greedy.", n, EXHAUSTIVE_MAX_N
        )
        result = solve_greedy(problem)
        result["strategy"] = "greedy_fallback"
        return result

    best_placement = [0] * n
    best_cost      = evaluate_qubo(best_placement, Q)
    n_evaluated    = 0

    for bits in itertools.product([0, 1], repeat=n):
        placement = list(bits)
        cost = evaluate_qubo(placement, Q)
        n_evaluated += 1
        if cost < best_cost:
            best_cost      = cost
            best_placement = placement

    return {
        "placement":   best_placement,
        "qubo_cost":   best_cost,
        "strategy":    "exhaustive",
        "valid":       True,
        "n_evaluated": n_evaluated,
    }


# ---------------------------------------------------------------------------
# Comparison helper
# ---------------------------------------------------------------------------

def compare_results(
    quantum_result: dict,
    classical_result: dict,
    tolerance: float = 0.15,
) -> dict:
    """
    Compare quantum and classical placements.

    A quantum result 'matches' the classical answer if:
      1. The QUBO objective values are within `tolerance` of each other
         (relative to the classical cost magnitude), OR
      2. The placements are identical.

    Returns
    -------
    dict with keys:
        match           — bool
        quantum_cost    — float
        classical_cost  — float
        cost_gap        — float (|Q_cost - C_cost|)
        relative_gap    — float (cost_gap / max(|C_cost|, 1e-9))
        placements_equal — bool
        verdict         — str  human-readable summary
    """
    q_cost = quantum_result.get("qubo_cost", float("inf"))
    c_cost = classical_result.get("qubo_cost", float("inf"))
    q_placement = quantum_result.get("placement", [])
    c_placement = classical_result.get("placement", [])

    cost_gap     = abs(q_cost - c_cost)
    relative_gap = cost_gap / max(abs(c_cost), 1e-9)
    placements_equal = (q_placement == c_placement)

    match = placements_equal or (relative_gap <= tolerance)

    if placements_equal:
        verdict = "MATCH — identical placements"
    elif relative_gap <= tolerance:
        verdict = f"MATCH — costs within {relative_gap:.1%} of classical optimum"
    else:
        verdict = f"MISMATCH — quantum cost {relative_gap:.1%} worse than classical"

    return {
        "match":            match,
        "quantum_cost":     q_cost,
        "classical_cost":   c_cost,
        "cost_gap":         cost_gap,
        "relative_gap":     relative_gap,
        "placements_equal": placements_equal,
        "verdict":          verdict,
    }
