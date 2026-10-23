"""
@team: Boeing Group 1
@contributors: [Zach Merkel]

This is an implementation of the classical solver using hardcoded networks,
network input from the frontend/simulation layer will be implemented in future sprints.
"""
from ortools.sat.python import cp_model


nodes = [
    {"ip": "A", "base": 0.2, "risk": 0.5},
    {"ip": "B", "base": 0.2, "risk": 0.5},
    {"ip": "C", "base": 0.2, "risk": 0.5},
]

#links that the one way devices can be placed on
links = [("A","B"), ("B","A"), ("B","C"), ("C","B")]   # directed

devices = [
    {"id": "fw0", "modifier": 0.3, "mode": "one_way"},
    {"id": "fw1", "modifier": 0.3, "mode": "both"},
]

#Note: probably want to move this to a file shared by the classical and brute force solver.
#Takes in a device and a link and determines which nodes are protected by placing it there
#This is a temporary and simplified implementation that assumes devices protect only the nodes they touch
def covered_by(d, spot):
    if d["mode"] == "one_way":
        a, b = spot
        return {b}          # receiving end
    return set(spot)        # cable: both endpoints






#creates the "cables" that the two way devices can be placed on
cables = sorted({tuple(sorted(l)) for l in links})



x = {}

#determines where a device can be placed based on if it is both or one_way
for d in devices:
    spots = links if d["mode"] == "one_way" else cables
    for s in spots:
        x[d["id"], s] = model.NewBoolVar(f"x_{d['id']}_{s[0]}_{s[1]}")


#every device is placed exactly once
for d in devices:
    spots = links if d["mode"] == "one_way" else cables
    model.AddExactlyOne([x[d["id"], s] for s in spots])

#each link holds at most one device (accounts for one way and two way)
for (a, b) in links:
    cable = tuple(sorted((a, b)))
    occupying = []
    for d in devices:
        if d["mode"] == "one_way":
            occupying.append(x[d["id"], (a, b)])
        else:
            occupying.append(x[d["id"], cable])
    model.AddAtMostOne(occupying)


SCALE = 1000
#floats have to be scaled becasue the solver can only use integers
def q(v): return round(v * SCALE)

#gap is defined as risk - security_level
gaps = {}

for n in nodes:
    level = q(n["base"])
    for d in devices:
        #look at each device and check if it contributes to the security level
        spots = links if d["mode"] == "one_way" else cables
        #check each spot for the device
        for s in spots:
            if n["ip"] in covered_by(d, s):
                #create the formula for how much the sec level would be improved
                level += q(d["modifier"]) * x[d["id"], s]
    gap = model.NewIntVar(0, q(n["risk"]), f"gap_{n['ip']}")
    model.Add(gap + level >= q(n["risk"]))
    gaps[n["ip"]] = gap

#goal of the solver is to minimize the sum of the gaps
model.Minimize(sum(gaps.values()))
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10
status = solver.Solve(model)

#check the status
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    pass
else:
    pass

placement = {}
for (dev_id, spot), var in x.items():
    if solver.Value(var) == 1:
        placement[dev_id] = spot

levels = {n["ip"]: n["base"] for n in nodes}
for dev_id, spot in placement.items():
    d = next(d for d in devices if d["id"] == dev_id)
    for ip in covered_by(d, spot):
        levels[ip] += d["modifier"]