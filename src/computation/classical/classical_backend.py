"""
Translators between the simulation layer (NW_Structure / Simulation_Service)
and the classical solver (exec_classical).

exec_classical(nodes, links, devices) expects:
    nodes   : [{"ip": str, "base": float, "risk": float}, ...]
    links   : [(src_ip, dst_ip), ...]   directed, no duplicates, ip strings like "10.0.0.1"
    devices : [{"id": str, "mode": "one_way" | "both", "modifier": float}, ...]
and returns:
    {"status": str, "placement": {dev_id: (ip, ip)} | None,
     "levels": {ip: float} | None, "objective": int | None}
"""

from NW_Structure import NW_Node, NW_Sec_Device
from Simulation_Service import Simulation_Service
from solver_utils import covered_by
from classical import exec_classical


def _ip_str(ip_list):
    return ".".join(str(b) for b in ip_list)

def network_to_solver_input(sim):
    """Flatten a Simulation_Service into the (nodes, links) the solver takes."""
    nodes, links = [], set()
    for n in sim.node_list:
        if isinstance(n, NW_Sec_Device):
            continue  # security devices are what the solver places, not part of the input network
        ip = n.get_ip_str()
        nodes.append({"ip": ip, "base": n.base_sec_level, "risk": n.risk_level})
        for dest_ip, _cost, _bw, _proto, _port in n.connections:
            #most of these unused for now but will be implemented in future.
            links.add((ip, _ip_str(dest_ip)))
    return nodes, sorted(links)


# this will need updates
def devices_to_solver_input(sec_devices, modes=None, default_mode="both"):
    """
    Build the solver's device list from the available NW_Sec_Device objects.
    NW_Sec_Device has no one-way/both-directions attribute, so mode comes from
    `modes` ({device_type: "one_way" | "both"}) or default_mode.
    """

    #for now just assuming all devices are both until we get passthrough working
    return [
        {"id": d.get_ip_str(), "mode": "both", "modifier": d.sec_modifier}
        for d in sec_devices
    ]


# ---------------------------------------------------------------- solver -> network

def solver_output_to_network(sim, sec_devices, devices, result):
    """
    Build a new Simulation_Service from the solver result: copies of the original nodes with the
    solved security levels, plus the placed security devices with covered_devices filled in.
    `devices` is the list that was passed to the solver (needed for covered_by).
    """
    if result["placement"] is None:
        raise ValueError("solver found no placement (status: {})".format(result["status"]))

    new_sim = Simulation_Service(sim.sim_id)

    by_ip = {}
    for n in sim.node_list:
        if isinstance(n, NW_Sec_Device):
            continue
        copy = NW_Node(
            n.device_type, list(n.device_ip), n.base_sec_level, n.risk_level,
            connections=[(list(c[0]),) + tuple(c[1:]) for c in n.connections],  # explicit list: avoids the shared default
        )
        copy.security_level = result["levels"][n.get_ip_str()]
        new_sim.create_node(copy)
        by_ip[n.get_ip_str()] = copy

    dev_specs = {d["id"]: d for d in devices}
    sec_by_id = {d.get_ip_str(): d for d in sec_devices}
    for dev_id, spot in result["placement"].items():
        src = sec_by_id[dev_id]
        covered = [by_ip[ip] for ip in covered_by(dev_specs[dev_id], spot)]
        placed = NW_Sec_Device(
            src.device_type, list(src.device_ip), src.base_sec_level, src.risk_level, src.sec_modifier,
            covered_devices=[(node, list(node.device_ip)) for node in covered],
            connections=[],
        )
        new_sim.create_device(placed) #UNIMPLEMENTED
        new_sim.node_list.append(placed)

    return new_sim


def build_api_response(new_sim, result):
    """
    Payload for the API. The state string alone doesn't carry which link each device sits on
    (or sec_modifier/covered_devices), so the placement travels next to it.
    """
    return {
        "status": result["status"],
        "objective": result["objective"],
        "state": new_sim.get_sim_state(),
        "placement": {dev_id: list(spot) for dev_id, spot in result["placement"].items()},
    }

def run_classical(state_str):
    sim = Simulation_Service("id")
    nodes, links = network_to_solver_input(sim)
    
    ###STILL NEED SOME WAY TO GET DEVICES
    devices = devices_to_solver_input()

    results = exec_classical(nodes, links, devices)

