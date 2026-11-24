"""
@team: Boeing Group 1
@contributors: [Zach Merkel]

Brute force reference solver. It tries every possible placement of the devices
and keeps the best one, so it is only usable on very small networks. It takes the
same inputs and returns the same format as exec_classical, so the two can be
compared directly by the tests.
"""
from itertools import product

from solver_utils import scale_float, covered_by

def exec_brute_force(nodes, links, devices):
    #same "cables" the classical solver uses for two way devices
    cables = sorted({tuple(sorted(l)) for l in links})

    #the places each device is allowed to go
    options = []
    for d in devices:
        options.append(links if d["mode"] == "one_way" else cables)

    best_placement = None
    best_objective = None

    #product gives every combination of one spot per device
    for combo in product(*options):
        #work out which directed links each device takes up
        taken = []
        for d, s in zip(devices, combo):
            if d["mode"] == "one_way":
                taken.append(s)
            else:
                taken.extend(l for l in links if tuple(sorted(l)) == s)

        #a directed link can only hold one device, skip placements that break that
        if len(taken) != len(set(taken)):
            continue

        #total gap for this placement (scaled integers, same as the classical model)
        objective = 0
        for n in nodes:
            level = scale_float(n["base"])
            for d, s in zip(devices, combo):
                if n["ip"] in covered_by(d, s):
                    level += scale_float(d["modifier"])
            #going above risk provides no extra value so trim it
            objective += max(0, scale_float(n["risk"]) - level)

        if best_objective is None or objective < best_objective:
            best_objective = objective
            best_placement = {d["id"]: s for d, s in zip(devices, combo)}

    #no legal placement exists (for example more devices than places to put them)
    if best_placement is None:
        return {"status": "INFEASIBLE", "placement": None, "levels": None, "objective": None}

    levels = {n["ip"]: n["base"] for n in nodes}
    for dev_id, spot in best_placement.items():
        d = next(d for d in devices if d["id"] == dev_id)
        for ip in covered_by(d, spot):
            levels[ip] += d["modifier"]

    return {"status": "OPTIMAL", "placement": best_placement, "levels": levels, "objective": best_objective}