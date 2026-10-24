"""
@team: Boeing Group 1
@contributors: [Zach Merkel]

Runs a few small toy networks with hand-calculated answers through both the brute
force solver and the classical solver.

The expected value is the total gap, scaled by 1000 (so 300 means 0.3), or None if
no legal placement should exist. Several placements can be equally good, so only the
total gap is checked, the placement is just printed.
"""
import sys

from classical import exec_classical
from bruteforce import exec_brute_force


def node(ip, base=0.2, risk=0.5):
    return {"ip": ip, "base": base, "risk": risk}

#unless noted, every node starts at 0.2 with a target of 0.5, so an unprotected node is 300 short
LINE_NODES = [node("A"), node("B"), node("C")]
LINE_LINKS = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]   # A - B - C, both directions

FW0 = {"id": "fw0", "modifier": 0.3, "mode": "one_way"}   # fixes the one node it points at
FW1 = {"id": "fw1", "modifier": 0.3, "mode": "both"}      # fixes both ends of a cable

#name, nodes, links, devices, expected total gap
TESTS = [
    #3 nodes x 300 short = 900, a one way device fixes one node
    ("line, one way device only", LINE_NODES, LINE_LINKS, [FW0], 600),

    #a two way device fixes two nodes
    ("line, two way device only", LINE_NODES, LINE_LINKS, [FW1], 300),

    #two way covers two nodes, one way covers the third
    ("line, both devices", LINE_NODES, LINE_LINKS, [FW0, FW1], 0),

    #B already meets its target (base 0.2, risk 0.2), so only A and C are short (600 total),
    #and the one way device can fix only one of them
    ("line, middle node already safe", [node("A"), node("B", risk=0.2), node("C")], LINE_LINKS, [FW0], 300),

    #only an A->B link exists, a one way device on it protects B (the receiver), leaving A 300 short
    ("single direction link, one way device", [node("A"), node("B")], [("A", "B")], [FW0], 300),

    #two one way devices but only one directed link to put them on
    ("too many devices", [node("A"), node("B")], [("A", "B")], [FW0, {"id": "fw2", "modifier": 0.3, "mode": "one_way"}], None),
]


failures = 0
for name, nodes, links, devices, expected in TESTS:
    for solver_name, solve in (("brute force", exec_brute_force), ("classical", exec_classical)):
        result = solve(nodes, links, devices)
        if expected is None:
            ok = result["status"] == "INFEASIBLE"
        else:
            ok = result["status"] == "OPTIMAL" and result["objective"] == expected
        if not ok:
            failures += 1
        print(f"{'PASS' if ok else 'FAIL'}  {name} [{solver_name}]: expected {expected}, "
              f"got {result['objective']} ({result['status']}), placement {result['placement']}")

print(f"\n{'all tests passed' if failures == 0 else str(failures) + ' check(s) failed'}")