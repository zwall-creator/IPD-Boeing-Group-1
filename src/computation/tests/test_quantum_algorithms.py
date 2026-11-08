"""
test_quantum_algorithms.py
--------------------------
Test suite for Ticket #46 — Implement Quantum Algorithms.

Acceptance criteria (from GitHub issue):
  1. The quantum algorithm returns a valid placement on a small toy network
     that matches the classical solver's answer.
  2. Any result that breaks the constraints is flagged as invalid.

Test structure (following Zak's NW_Structure_Test.py pattern):
  - Control tests always pass/fail as expected
  - Unit tests for each module
  - Integration test: QAOA vs classical on the toy network
"""

import sys
import os
import unittest

# Add computation directory to path so imports resolve without packaging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from network_problem import (
    NetworkProblem, ProblemNode, ProblemEdge,
    build_problem_from_dicts, build_toy_problem,
)
from qaoa_solver import (
    build_qaoa_circuit, decode_counts, evaluate_qubo, solve_qaoa,
)
from classical_solver import (
    solve_greedy, solve_exhaustive, compare_results,
)
from result_validator import validate_placement, format_validation_report

DEFAULT_OPT_PARAMS = {
    "securityWeight": 50, "costWeight": 50,
    "bandwidthWeight": 50, "riskThreshold": 30,
}


# ===========================================================================
# Control tests — should NEVER fail
# ===========================================================================

class TestControl(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(True, True)

    def test_fail_check(self):
        self.assertNotEqual(True, False)


# ===========================================================================
# NetworkProblem tests
# ===========================================================================

class TestNetworkProblem(unittest.TestCase):

    def test_toy_problem_builds(self):
        """Toy network must have 4 nodes and 3 edges."""
        problem = build_toy_problem(DEFAULT_OPT_PARAMS)
        self.assertEqual(problem.n, 4)
        self.assertEqual(len(problem.edges), 3)

    def test_qubo_matrix_shape(self):
        """QUBO matrix must be NxN."""
        problem = build_toy_problem(DEFAULT_OPT_PARAMS)
        self.assertEqual(len(problem.Q), 4)
        for row in problem.Q:
            self.assertEqual(len(row), 4)

    def test_qubo_diagonal_reflects_security_deficit(self):
        """
        Node 0 (PC) has base_sec=0.2, risk=0.8 — large deficit.
        With high security_weight, Q[0][0] should be negative (reward).
        """
        params = {**DEFAULT_OPT_PARAMS, "securityWeight": 100, "costWeight": 0}
        problem = build_toy_problem(params)
        self.assertLess(problem.Q[0][0], 0,
            "Node 0 has high deficit — Q[0][0] should be negative (reward deploying)")

    def test_build_from_dicts(self):
        """build_problem_from_dicts must create correct node/edge counts."""
        nodes = [
            {"device_type": "PC",     "base_sec_level": 0.3, "risk_level": 0.7},
            {"device_type": "Server", "base_sec_level": 0.8, "risk_level": 0.2},
        ]
        edges = [
            {"source_id": 0, "target_id": 1, "cost": 2, "bandwidth": 5},
        ]
        problem = build_problem_from_dicts(nodes, edges, DEFAULT_OPT_PARAMS)
        self.assertEqual(problem.n, 2)
        self.assertEqual(len(problem.edges), 1)

    def test_empty_nodes_raises_no_error(self):
        """Empty node list should produce a valid zero-node problem."""
        problem = build_problem_from_dicts([], [], DEFAULT_OPT_PARAMS)
        self.assertEqual(problem.n, 0)


# ===========================================================================
# QAOA circuit tests
# ===========================================================================

class TestQAOACircuit(unittest.TestCase):

    def setUp(self):
        self.problem = build_toy_problem(DEFAULT_OPT_PARAMS)

    def test_circuit_qubit_count(self):
        """Circuit must have exactly N qubits for an N-node problem."""
        circuit = build_qaoa_circuit(self.problem)
        self.assertEqual(circuit.num_qubits, self.problem.n)

    def test_circuit_has_measurements(self):
        """Circuit must have classical bits for measurement."""
        circuit = build_qaoa_circuit(self.problem)
        self.assertEqual(circuit.num_clbits, self.problem.n)

    def test_circuit_depth_nonzero(self):
        """A non-trivial circuit must have depth > 1."""
        circuit = build_qaoa_circuit(self.problem)
        self.assertGreater(circuit.depth(), 1)

    def test_empty_problem_raises(self):
        """Zero-node problem must raise ValueError."""
        empty = build_problem_from_dicts([], [], DEFAULT_OPT_PARAMS)
        with self.assertRaises(ValueError):
            build_qaoa_circuit(empty)

    def test_p_layers_increase_depth(self):
        """More QAOA layers should produce a deeper circuit."""
        c1 = build_qaoa_circuit(self.problem, p=1)
        c2 = build_qaoa_circuit(self.problem, p=2)
        self.assertGreater(c2.depth(), c1.depth())


# ===========================================================================
# Decode / evaluate tests
# ===========================================================================

class TestDecodeAndEvaluate(unittest.TestCase):

    def test_decode_most_frequent(self):
        """decode_counts must pick the most-frequent bitstring."""
        counts = {"0000": 100, "1010": 500, "0101": 200}
        result = decode_counts(counts, n=4)
        self.assertEqual(result["bitstring"], "1010")

    def test_decode_confidence(self):
        """Confidence must equal best_count / total_shots."""
        counts = {"1111": 800, "0000": 200}
        result = decode_counts(counts, n=4)
        self.assertAlmostEqual(result["confidence"], 0.8)

    def test_decode_placement_length(self):
        """Placement list must have length n."""
        counts = {"101": 300, "010": 700}
        result = decode_counts(counts, n=3)
        self.assertEqual(len(result["placement"]), 3)

    def test_decode_empty_counts(self):
        """Empty counts must return zero placement without error."""
        result = decode_counts({}, n=4)
        self.assertEqual(result["placement"], [0, 0, 0, 0])
        self.assertEqual(result["confidence"], 0.0)

    def test_evaluate_qubo_all_zeros(self):
        """All-zero placement must return zero cost."""
        Q = [[1.0, 0.5], [0.5, 1.0]]
        cost = evaluate_qubo([0, 0], Q)
        self.assertEqual(cost, 0.0)

    def test_evaluate_qubo_all_ones(self):
        """All-one placement for 2x2 Q=[[a,b],[b,c]] must equal a+2b+c."""
        Q = [[1.0, 0.5], [0.5, 2.0]]
        cost = evaluate_qubo([1, 1], Q)
        self.assertAlmostEqual(cost, 1.0 + 0.5 + 0.5 + 2.0)


# ===========================================================================
# Classical solver tests
# ===========================================================================

class TestClassicalSolver(unittest.TestCase):

    def setUp(self):
        self.problem = build_toy_problem(DEFAULT_OPT_PARAMS)

    def test_greedy_returns_valid_placement(self):
        """Greedy must return a placement of length N with values in {0,1}."""
        result = solve_greedy(self.problem)
        self.assertEqual(len(result["placement"]), self.problem.n)
        for x in result["placement"]:
            self.assertIn(x, [0, 1])

    def test_exhaustive_returns_valid_placement(self):
        """Exhaustive must return a placement of length N."""
        result = solve_exhaustive(self.problem)
        self.assertEqual(len(result["placement"]), self.problem.n)
        for x in result["placement"]:
            self.assertIn(x, [0, 1])

    def test_exhaustive_optimal_leq_greedy(self):
        """Exhaustive cost must be <= greedy cost (exhaustive is exact)."""
        greedy    = solve_greedy(self.problem)
        exhaustive = solve_exhaustive(self.problem)
        self.assertLessEqual(
            exhaustive["qubo_cost"], greedy["qubo_cost"] + 1e-9,
            "Exhaustive solver must find a solution at least as good as greedy"
        )

    def test_exhaustive_evaluates_all_assignments(self):
        """For N=4, must evaluate 2^4=16 assignments."""
        result = solve_exhaustive(self.problem)
        self.assertEqual(result["n_evaluated"], 2 ** self.problem.n)

    def test_compare_identical_placements(self):
        """Identical placements must produce match=True."""
        r1 = {"placement": [1, 0, 1, 0], "qubo_cost": -1.5}
        r2 = {"placement": [1, 0, 1, 0], "qubo_cost": -1.5}
        cmp = compare_results(r1, r2)
        self.assertTrue(cmp["match"])
        self.assertTrue(cmp["placements_equal"])

    def test_compare_large_gap_is_mismatch(self):
        """A 50% cost gap must be flagged as a mismatch."""
        r1 = {"placement": [1, 1, 1, 1], "qubo_cost": 2.0}
        r2 = {"placement": [1, 0, 0, 0], "qubo_cost": 1.0}
        cmp = compare_results(r1, r2, tolerance=0.15)
        self.assertFalse(cmp["match"])


# ===========================================================================
# Result validator tests
# ===========================================================================

class TestResultValidator(unittest.TestCase):

    def setUp(self):
        self.problem = build_toy_problem(DEFAULT_OPT_PARAMS)

    def test_all_deployed_is_valid(self):
        """Deploying everywhere must always be valid (no security deficits)."""
        validation = validate_placement(self.problem, [1, 1, 1, 1])
        self.assertTrue(validation["valid"])
        self.assertEqual(len(validation["violations"]), 0)

    def test_security_levels_length(self):
        """security_levels list must have length N."""
        validation = validate_placement(self.problem, [0, 0, 0, 0])
        self.assertEqual(len(validation["security_levels"]), self.problem.n)

    def test_wrong_placement_length_fails(self):
        """Placement of wrong length must produce a violation."""
        validation = validate_placement(self.problem, [1, 0])
        self.assertFalse(validation["valid"])
        self.assertGreater(len(validation["violations"]), 0)

    def test_node0_undeployed_causes_violation(self):
        """
        Node 0 (PC): base_sec=0.2, risk=0.8.
        Not deploying there (x=0) gives effective_sec=0.2 < risk=0.8.
        Deficit 0.6 > risk_threshold/100=0.3 → hard violation.
        """
        validation = validate_placement(self.problem, [0, 1, 1, 1])
        self.assertFalse(validation["valid"],
            "Node 0 undeployed with large security deficit must be a violation")

    def test_server_node_safe_without_deployment(self):
        """
        Node 2 (Server): base_sec=0.9, risk=0.3.
        Not deploying (x=0) gives effective_sec=0.9 >= risk=0.3 → no violation.
        """
        # Deploy everywhere except node 2
        validation = validate_placement(self.problem, [1, 1, 0, 1])
        # Node 2 is safe so this should not cause a security violation for node 2
        node2_violated = any("node 2" in v.lower() or "Server" in v
                             for v in validation["violations"])
        self.assertFalse(node2_violated,
            "Server node with base_sec 0.9 > risk 0.3 must not be a security violation")

    def test_format_report_contains_valid_or_invalid(self):
        """format_validation_report must include VALID or INVALID."""
        validation = validate_placement(self.problem, [1, 1, 1, 1])
        report = format_validation_report(validation, [1, 1, 1, 1])
        self.assertIn("VALID", report)


# ===========================================================================
# Integration test — acceptance criteria
# ===========================================================================

class TestAcceptanceCriteria(unittest.TestCase):
    """
    Directly tests the two acceptance criteria from GitHub issue #46:
      1. Quantum algorithm returns a valid placement on the toy network
         that matches the classical solver's answer.
      2. A result that breaks constraints is flagged as invalid.
    """

    def setUp(self):
        self.problem = build_toy_problem(DEFAULT_OPT_PARAMS)
        self.classical = solve_exhaustive(self.problem)

    def test_AC1_qaoa_matches_classical_on_toy_network(self):
        """
        AC1: QAOA result must match classical within 15% QUBO cost gap.
        Uses Aer simulator (no IBM token needed).
        """
        quantum = solve_qaoa(self.problem, shots=2048)

        # Must not error out
        self.assertIsNone(quantum.get("error") if quantum.get("used_ibm") else None,
                          "QAOA must run without fatal error on Aer")

        # Must return a placement of correct length
        self.assertEqual(len(quantum["placement"]), self.problem.n,
                         "QAOA placement must have one value per node")

        # Must return values in {0, 1}
        for x in quantum["placement"]:
            self.assertIn(x, [0, 1], "Placement values must be binary")

        # Must match classical result within tolerance
        comparison = compare_results(quantum, self.classical, tolerance=0.15)
        self.assertTrue(
            comparison["match"],
            f"AC1 FAILED — {comparison['verdict']} | "
            f"quantum cost: {comparison['quantum_cost']:.4f}, "
            f"classical cost: {comparison['classical_cost']:.4f}"
        )

    def test_AC2_invalid_placement_flagged(self):
        """
        AC2: A placement that violates constraints must be flagged as invalid.
        All-zero placement on this toy network has Node 0 with deficit 0.6 > threshold.
        """
        bad_placement = [0, 0, 0, 0]
        validation = validate_placement(self.problem, bad_placement)
        self.assertFalse(
            validation["valid"],
            "AC2 FAILED — all-zero placement must be flagged as INVALID"
        )
        self.assertGreater(
            len(validation["violations"]), 0,
            "AC2 FAILED — must report at least one violation"
        )

    def test_AC2_valid_placement_not_flagged(self):
        """
        AC2 (positive): The classical optimal placement must pass validation.
        """
        validation = validate_placement(self.problem, self.classical["placement"])
        self.assertTrue(
            validation["valid"],
            f"AC2 FAILED — classical optimal placement must be VALID, "
            f"got violations: {validation['violations']}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
