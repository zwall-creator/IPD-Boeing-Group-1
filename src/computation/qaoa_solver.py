"""
qaoa_solver.py
--------------
Implements a QAOA (Quantum Approximate Optimisation Algorithm) circuit
that encodes the network placement QUBO and finds an approximate solution.

Algorithm overview
------------------
QAOA for an N-node problem uses N qubits. Each qubit i represents whether
node i receives a security resource (|1⟩) or not (|0⟩).

The circuit alternates p layers of:
  1. Cost unitary  U_C(γ) — applies phase proportional to the QUBO objective
  2. Mixer unitary U_B(β) — applies Pauli-X rotations to explore the space

For this implementation we use p=1 (one QAOA layer) which is sufficient for
small networks and gives deterministic, reproducible results on the simulator.

After sampling, the most-frequent bitstring is decoded as the placement:
  bitstring[i] = '1'  →  deploy resource to node i
  bitstring[i] = '0'  →  no resource

References
----------
Farhi et al., "A Quantum Approximate Optimization Algorithm" (2014)
"""

from __future__ import annotations
import logging
import math
from typing import Optional

from qiskit import QuantumCircuit
from network_problem import NetworkProblem

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# QAOA circuit builder
# ---------------------------------------------------------------------------

def build_qaoa_circuit(
    problem: NetworkProblem,
    gamma: float = 0.4,
    beta:  float = 0.3,
    p:     int   = 1,
) -> QuantumCircuit:
    """
    Build a p-layer QAOA circuit for the given NetworkProblem.

    Parameters
    ----------
    problem : NetworkProblem
        Must have build_qubo() already called (Q matrix populated).
    gamma   : float
        Cost unitary angle (radians). Controls problem encoding strength.
    beta    : float
        Mixer unitary angle (radians). Controls exploration width.
    p       : int
        Number of QAOA layers. p=1 is sufficient for small problems.

    Returns
    -------
    QuantumCircuit with n qubits and n classical bits, ready to run.
    """
    n = problem.n
    Q = problem.Q

    if n == 0:
        raise ValueError("NetworkProblem has no nodes — cannot build circuit")

    qc = QuantumCircuit(n, n)

    # ------------------------------------------------------------------
    # Initial state: equal superposition |+⟩^n via Hadamard on all qubits
    # ------------------------------------------------------------------
    qc.h(range(n))

    for _ in range(p):
        # ------------------------------------------------------------------
        # Cost unitary U_C(γ):
        #   For each diagonal term Q[i][i]: apply Rz(2γ Q[i][i]) to qubit i
        #   For each off-diagonal term Q[i][j]: apply ZZ coupling via
        #     CNOT-Rz-CNOT decomposition
        # ------------------------------------------------------------------
        for i in range(n):
            angle = 2 * gamma * Q[i][i]
            if abs(angle) > 1e-9:
                qc.rz(angle, i)

        for i in range(n):
            for j in range(i + 1, n):
                coupling = Q[i][j]
                if abs(coupling) > 1e-9:
                    angle = 2 * gamma * coupling
                    # ZZ interaction: CNOT(i→j) · Rz(angle, j) · CNOT(i→j)
                    qc.cx(i, j)
                    qc.rz(angle, j)
                    qc.cx(i, j)

        # ------------------------------------------------------------------
        # Mixer unitary U_B(β):
        #   Apply Rx(2β) to every qubit — standard X-mixer
        # ------------------------------------------------------------------
        for i in range(n):
            qc.rx(2 * beta, i)

    # ------------------------------------------------------------------
    # Measure all qubits
    # ------------------------------------------------------------------
    qc.measure(range(n), range(n))

    return qc


# ---------------------------------------------------------------------------
# Decode result
# ---------------------------------------------------------------------------

def decode_counts(
    counts: dict[str, int],
    n: int,
) -> dict:
    """
    Extract the best placement from a counts dictionary.

    The 'best' bitstring is the most-frequently measured outcome.
    Returns a dict with:
        placement   — list[int] of length n, values 0 or 1
        bitstring   — str e.g. '1010'
        confidence  — float fraction of shots that agreed on this answer
        all_counts  — the raw counts dict
    """
    if not counts:
        return {
            "placement":  [0] * n,
            "bitstring":  "0" * n,
            "confidence": 0.0,
            "all_counts": counts,
        }

    total_shots = sum(counts.values())
    best_bitstring = max(counts, key=counts.get)
    best_count     = counts[best_bitstring]

    # Qiskit orders bits right-to-left (qubit 0 = rightmost character)
    # Reverse so placement[i] corresponds to qubit i
    normalised = best_bitstring.zfill(n)[::-1]
    placement  = [int(b) for b in normalised]

    return {
        "placement":  placement,
        "bitstring":  best_bitstring,
        "confidence": best_count / total_shots,
        "all_counts": counts,
    }


def evaluate_qubo(placement: list[int], Q: list[list[float]]) -> float:
    """
    Compute the QUBO objective value x^T Q x for a given placement.
    Lower is better.
    """
    n = len(placement)
    cost = 0.0
    for i in range(n):
        for j in range(n):
            cost += placement[i] * Q[i][j] * placement[j]
    return cost


# ---------------------------------------------------------------------------
# Top-level solver
# ---------------------------------------------------------------------------

def solve_qaoa(
    problem: NetworkProblem,
    shots:   int   = 1024,
    gamma:   float = 0.4,
    beta:    float = 0.3,
    p:       int   = 1,
    run_circuit_fn = None,
) -> dict:
    """
    Run the full QAOA pipeline for a NetworkProblem.

    Parameters
    ----------
    problem         : NetworkProblem  (with Q matrix built)
    shots           : int
    gamma, beta, p  : QAOA hyperparameters
    run_circuit_fn  : callable  — quantum_backend.run_circuit (injected to
                      avoid circular imports; defaults to importing it here)

    Returns
    -------
    dict with keys:
        placement       — list[int] (0/1 per node)
        bitstring       — str
        confidence      — float
        qubo_cost       — float (objective value of chosen placement)
        backend         — str
        used_ibm        — bool
        error           — str | None
        circuit_depth   — int
        n_qubits        — int
    """
    if run_circuit_fn is None:
        from quantum_backend import run_circuit as run_circuit_fn

    # Build the QAOA circuit
    try:
        circuit = build_qaoa_circuit(problem, gamma=gamma, beta=beta, p=p)
    except Exception as exc:
        log.error("Failed to build QAOA circuit: %s", exc)
        return {
            "placement": [0] * problem.n,
            "bitstring": "0" * problem.n,
            "confidence": 0.0,
            "qubo_cost": float("inf"),
            "backend": "none",
            "used_ibm": False,
            "error": f"Circuit build failed: {exc}",
            "circuit_depth": 0,
            "n_qubits": problem.n,
        }

    circuit_depth = circuit.depth()

    # Run on quantum backend (IBM or Aer)
    result = run_circuit_fn(circuit, shots=shots)

    if not result["counts"]:
        return {
            "placement": [0] * problem.n,
            "bitstring": "0" * problem.n,
            "confidence": 0.0,
            "qubo_cost": float("inf"),
            "backend": result.get("backend", "none"),
            "used_ibm": result.get("used_ibm", False),
            "error": result.get("error", "No counts returned"),
            "circuit_depth": circuit_depth,
            "n_qubits": problem.n,
        }

    # Decode the best measurement outcome
    decoded = decode_counts(result["counts"], problem.n)
    qubo_cost = evaluate_qubo(decoded["placement"], problem.Q)

    return {
        "placement":     decoded["placement"],
        "bitstring":     decoded["bitstring"],
        "confidence":    decoded["confidence"],
        "qubo_cost":     qubo_cost,
        "backend":       result["backend"],
        "used_ibm":      result["used_ibm"],
        "error":         result.get("error"),
        "circuit_depth": circuit_depth,
        "n_qubits":      problem.n,
        "all_counts":    decoded["all_counts"],
    }
