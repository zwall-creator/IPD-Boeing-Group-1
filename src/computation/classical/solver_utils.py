"""
@team: Boeing Group 1
@contributors: [Zach Merkel]

Utility functions used by solvers
"""

SCALE = 1000
#floats have to be scaled becasue the solver can only use integers
def scale_float(v): return round(v * SCALE)


#Takes in a device and a link and determines which nodes are protected by placing it there
#This is a temporary and simplified implementation that assumes devices protect only the nodes they touch
def covered_by(d, spot):
    if d["mode"] == "one_way":
        a, b = spot
        return {b}          # receiving end
    return set(spot)        # cable: both endpoints