"""
network_problem.py
------------------
Encodes a network topology (NW_Structure nodes + edges) as a Quadratic
Unconstrained Binary Optimisation (QUBO) problem suitable for QAOA.

Problem definition
------------------
Given a set of N network nodes, each with a base_sec_level and risk_level,
and a set of directed edges with cost and bandwidth, find a binary assignment
x_i ∈ {0, 1} for each node where:

    x_i = 1  →  deploy a security resource to node i (raises security_level)
    x_i = 0  →  no extra resource deployed

Objective (minimise):
    - Penalise nodes where security_level < risk_level  (security deficit)
    - Penalise total deployment cost                     (resource cost)
    - Penalise bandwidth violations on edges             (congestion)
    - Reward high-security coverage                      (security weight)

QUBO form:
    min  x^T Q x
where Q is an NxN upper-triangular matrix (diagonal = linear terms,
off-diagonal = quadratic coupling terms).

The weights (security_weight, cost_weight, bandwidth_weight, risk_threshold)
from the frontend sliders map directly to the QUBO penalty coefficients.
"""

from __future__ import annotations
import sys
import os
import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes — mirror of NW_Structure but serialisable without import issues
# ---------------------------------------------------------------------------

@dataclass
class ProblemNode:
    """Lightweight representation of a network node for optimisation."""
    node_id:        int
    device_type:    str
    ip:             list            # [a, b, c, d]
    base_sec_level: float
    risk_level:     float
    # Derived after placement
    security_level: float = field(init=False)

    def __post_init__(self):
        self.security_level = self.base_sec_level


@dataclass
class ProblemEdge:
    """Lightweight representation of a directed edge."""
    source_id:       int
    target_id:       int
    cost:            int   = 1
    bandwidth:       int   = 1
    connection_type: str   = 'TCP'


@dataclass
class NetworkProblem:
    """
    Full QUBO-ready description of the optimisation problem.

    Attributes
    ----------
    nodes : list[ProblemNode]
    edges : list[ProblemEdge]
    n     : int  — number of nodes (== number of qubits in QAOA)
    Q     : list[list[float]]  — NxN QUBO matrix
    """
    nodes:              list
    edges:              list
    security_weight:    float = 50.0
    cost_weight:        float = 50.0
    bandwidth_weight:   float = 50.0
    risk_threshold:     float = 30.0

    # Populated by build_qubo()
    n: int               = field(init=False, default=0)
    Q: list              = field(init=False, default_factory=list)

    def __post_init__(self):
        self.n = len(self.nodes)
        self.Q = [[0.0] * self.n for _ in range(self.n)]

    # ------------------------------------------------------------------
    # QUBO construction
    # ------------------------------------------------------------------

    def build_qubo(self) -> list[list[float]]:
        """
        Populate and return the NxN QUBO matrix Q.

        Linear terms  Q[i][i]: cost of assigning x_i = 1
        Quadratic terms Q[i][j] (i<j): coupling between nodes i and j

        Penalty structure:
          1. Security deficit  — if node i's base_sec_level < risk_level,
             NOT deploying there is penalised (negative diagonal = reward)
          2. Deployment cost   — proportional to edge costs touching node i
          3. Bandwidth penalty — edges where both endpoints are undeployed
             and bandwidth < threshold are penalised
          4. Cross-node reward — deploying on both ends of a high-cost edge
             reduces the coupling term (cost sharing)
        """
        # Normalise weights to [0, 1]
        sw = self.security_weight  / 100.0
        cw = self.cost_weight      / 100.0
        bw = self.bandwidth_weight / 100.0
        rt = self.risk_threshold   / 100.0   # fraction of max risk

        Q = self.Q

        # --- Linear terms (diagonal) ---
        for i, node in enumerate(self.nodes):
            sec_deficit = node.risk_level - node.base_sec_level
            # Positive deficit → reward deploying here (negative Q[i][i])
            Q[i][i] += -sw * max(0.0, sec_deficit)

            # Cost of deploying: sum of costs of edges touching this node
            node_cost = sum(
                e.cost for e in self.edges
                if e.source_id == i or e.target_id == i
            )
            Q[i][i] += cw * node_cost * 0.1   # scale down

        # --- Quadratic terms (off-diagonal) ---
        for e in self.edges:
            i, j = e.source_id, e.target_id
            if i >= self.n or j >= self.n:
                continue
            col = max(i, j)
            row = min(i, j)

            # Bandwidth penalty: if neither endpoint is secured and bandwidth
            # is low, penalise not covering this edge
            bw_penalty = bw * max(0.0, (10 - e.bandwidth)) * 0.05
            Q[row][col] += bw_penalty

            # Cost-sharing reward: deploying on both endpoints of a costly
            # edge is efficient — reduce the coupling term
            cost_share = -cw * e.cost * 0.05
            Q[row][col] += cost_share

        self.Q = Q
        return Q

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-serialisable summary of the problem."""
        return {
            "n_nodes":          self.n,
            "n_edges":          len(self.edges),
            "security_weight":  self.security_weight,
            "cost_weight":      self.cost_weight,
            "bandwidth_weight": self.bandwidth_weight,
            "risk_threshold":   self.risk_threshold,
            "qubo_diagonal":    [self.Q[i][i] for i in range(self.n)],
        }


# ---------------------------------------------------------------------------
# Builder functions
# ---------------------------------------------------------------------------

def build_problem_from_dicts(
    nodes: list[dict],
    edges: list[dict],
    opt_params: dict,
) -> NetworkProblem:
    """
    Build a NetworkProblem from the frontend's JSON node/edge lists.

    Node dict keys: id, device_type, ip (optional), base_sec_level, risk_level
    Edge dict keys: source_id, target_id, cost, bandwidth, connection_type
    """
    problem_nodes = []
    for i, nd in enumerate(nodes):
        problem_nodes.append(ProblemNode(
            node_id        = i,
            device_type    = nd.get("device_type", "PC"),
            ip             = nd.get("ip", [0, 0, 0, 0]),
            base_sec_level = float(nd.get("base_sec_level", 0.5)),
            risk_level     = float(nd.get("risk_level", 0.3)),
        ))

    problem_edges = []
    for ed in edges:
        problem_edges.append(ProblemEdge(
            source_id       = int(ed.get("source_id", 0)),
            target_id       = int(ed.get("target_id", 1)),
            cost            = int(ed.get("cost", 1)),
            bandwidth       = int(ed.get("bandwidth", 5)),
            connection_type = ed.get("connection_type", "TCP"),
        ))

    problem = NetworkProblem(
        nodes            = problem_nodes,
        edges            = problem_edges,
        security_weight  = float(opt_params.get("securityWeight", 50)),
        cost_weight      = float(opt_params.get("costWeight", 50)),
        bandwidth_weight = float(opt_params.get("bandwidthWeight", 50)),
        risk_threshold   = float(opt_params.get("riskThreshold", 30)),
    )
    problem.build_qubo()
    return problem


def build_toy_problem(opt_params: dict = None) -> NetworkProblem:
    """
    Construct a small 4-node toy network for testing and demos.

    Topology:
        PC (high risk) ──TCP──> Router ──TCP──> Server (high security)
                                  |
                              Switch (medium)

    This is the reference network for the acceptance criteria check.
    """
    if opt_params is None:
        opt_params = {"securityWeight": 50, "costWeight": 50,
                      "bandwidthWeight": 50, "riskThreshold": 30}

    nodes = [
        {"device_type": "PC",     "ip": [10,0,0,1], "base_sec_level": 0.2, "risk_level": 0.8},
        {"device_type": "Router", "ip": [10,0,0,2], "base_sec_level": 0.5, "risk_level": 0.5},
        {"device_type": "Server", "ip": [10,0,0,3], "base_sec_level": 0.9, "risk_level": 0.3},
        {"device_type": "Switch", "ip": [10,0,0,4], "base_sec_level": 0.4, "risk_level": 0.4},
    ]
    edges = [
        {"source_id": 0, "target_id": 1, "cost": 2, "bandwidth": 8,  "connection_type": "TCP"},
        {"source_id": 1, "target_id": 2, "cost": 1, "bandwidth": 10, "connection_type": "TCP"},
        {"source_id": 1, "target_id": 3, "cost": 3, "bandwidth": 4,  "connection_type": "TCP"},
    ]
    return build_problem_from_dicts(nodes, edges, opt_params)
