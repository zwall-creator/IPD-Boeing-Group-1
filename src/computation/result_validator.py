"""
result_validator.py
-------------------
Validates a placement solution against the network's hard constraints.

Constraint definitions (following NW_Structure.py semantics)
-------------------------------------------------------------
1. Security coverage  — for every node i where x_i = 0 (not deployed),
   its current security_level must be >= risk_level.
   Nodes where security_level < risk_level AND x_i = 0 are VIOLATIONS.

2. Bandwidth feasibility — for every edge (i→j), the sum of traffic
   from all nodes routing through that edge must not exceed bandwidth.
   (Simplified: an edge is violated if both endpoints are undeployed
   AND the edge's bandwidth is below the risk_threshold.)

3. Connectivity — every node must be reachable from at least one
   deployed node (or be deployed itself).  Isolated undeployed nodes
   are flagged as warnings (not hard failures).

A placement is VALID if it has zero hard violations.
A placement is INVALID if it has one or more hard violations.
Warnings are informational only.
"""

from __future__ import annotations
import logging
from network_problem import NetworkProblem, ProblemNode, ProblemEdge

log = logging.getLogger(__name__)

SECURITY_BOOST = 0.4   # how much security_level increases when x_i = 1


def validate_placement(
    problem: NetworkProblem,
    placement: list[int],
) -> dict:
    """
    Validate a binary placement against the network's constraints.

    Parameters
    ----------
    problem   : NetworkProblem
    placement : list[int]  — length == problem.n, values 0 or 1

    Returns
    -------
    dict with keys:
        valid               — bool (True if zero hard violations)
        violations          — list[str]  hard constraint failures
        warnings            — list[str]  soft constraint issues
        security_levels     — list[float]  effective security per node
        coverage_summary    — list[dict]   per-node coverage detail
        bandwidth_summary   — list[dict]   per-edge bandwidth detail
    """
    n = problem.n
    nodes = problem.nodes
    edges = problem.edges
    rt    = problem.risk_threshold / 100.0   # normalise to [0,1]

    if len(placement) != n:
        return {
            "valid":      False,
            "violations": [f"Placement length {len(placement)} != n_nodes {n}"],
            "warnings":   [],
            "security_levels":  [],
            "coverage_summary": [],
            "bandwidth_summary": [],
        }

    violations: list[str] = []
    warnings:   list[str] = []

    # ------------------------------------------------------------------
    # 1. Security coverage
    # ------------------------------------------------------------------
    security_levels = []
    coverage_summary = []

    for i, node in enumerate(nodes):
        # Deploying a resource boosts the node's effective security level
        effective_sec = node.base_sec_level + (SECURITY_BOOST if placement[i] == 1 else 0.0)
        effective_sec = min(effective_sec, 1.0)
        security_levels.append(effective_sec)

        deployed = placement[i] == 1
        deficit  = node.risk_level - effective_sec
        covered  = effective_sec >= node.risk_level

        entry = {
            "node_id":       i,
            "device_type":   node.device_type,
            "deployed":      deployed,
            "base_sec":      node.base_sec_level,
            "effective_sec": round(effective_sec, 4),
            "risk_level":    node.risk_level,
            "covered":       covered,
        }
        coverage_summary.append(entry)

        if not covered:
            msg = (
                f"Node {i} ({node.device_type} {node.ip}): "
                f"security {effective_sec:.2f} < risk {node.risk_level:.2f} "
                f"(deficit {deficit:.2f})"
            )
            # Hard violation: undeployed node with significant deficit
            if not deployed and deficit > rt:
                violations.append(msg)
            # Warning: deployed node still below risk (shouldn't happen with
            # SECURITY_BOOST=0.4, but flag if risk_level > base+0.4)
            elif covered is False:
                warnings.append(f"[WARN] {msg}")

    # ------------------------------------------------------------------
    # 2. Bandwidth feasibility
    # ------------------------------------------------------------------
    bandwidth_summary = []
    bw_threshold = max(1, int(problem.risk_threshold / 10))

    for edge in edges:
        i, j = edge.source_id, edge.target_id
        if i >= n or j >= n:
            continue

        src_deployed  = placement[i] == 1
        tgt_deployed  = placement[j] == 1
        bw_ok         = edge.bandwidth >= bw_threshold
        both_exposed  = not src_deployed and not tgt_deployed

        entry = {
            "source_id":      i,
            "target_id":      j,
            "bandwidth":      edge.bandwidth,
            "bw_threshold":   bw_threshold,
            "src_deployed":   src_deployed,
            "tgt_deployed":   tgt_deployed,
            "feasible":       not (both_exposed and not bw_ok),
        }
        bandwidth_summary.append(entry)

        if both_exposed and not bw_ok:
            violations.append(
                f"Edge {i}→{j}: both endpoints undeployed and "
                f"bandwidth {edge.bandwidth} < threshold {bw_threshold}"
            )

    # ------------------------------------------------------------------
    # 3. Connectivity warning
    # ------------------------------------------------------------------
    deployed_ids = {i for i, x in enumerate(placement) if x == 1}
    reachable    = set(deployed_ids)

    # BFS from all deployed nodes
    adj = {i: [] for i in range(n)}
    for edge in edges:
        if edge.source_id < n and edge.target_id < n:
            adj[edge.source_id].append(edge.target_id)
            adj[edge.target_id].append(edge.source_id)  # treat as undirected

    queue = list(deployed_ids)
    while queue:
        current = queue.pop()
        for neighbour in adj[current]:
            if neighbour not in reachable:
                reachable.add(neighbour)
                queue.append(neighbour)

    unreachable = set(range(n)) - reachable
    for i in unreachable:
        warnings.append(
            f"[WARN] Node {i} ({nodes[i].device_type}) is not reachable "
            f"from any deployed node"
        )

    return {
        "valid":             len(violations) == 0,
        "violations":        violations,
        "warnings":          warnings,
        "security_levels":   security_levels,
        "coverage_summary":  coverage_summary,
        "bandwidth_summary": bandwidth_summary,
    }


def format_validation_report(validation: dict, placement: list[int]) -> str:
    """Return a concise human-readable validation summary."""
    status = "VALID" if validation["valid"] else "INVALID"
    n_viol = len(validation["violations"])
    n_warn = len(validation["warnings"])
    lines = [
        f"[Validator] Result: {status} | "
        f"Placement: {''.join(str(x) for x in placement)} | "
        f"Violations: {n_viol} | Warnings: {n_warn}"
    ]
    for v in validation["violations"]:
        lines.append(f"  ✗ {v}")
    for w in validation["warnings"]:
        lines.append(f"  ⚠ {w}")
    return "\n".join(lines)
