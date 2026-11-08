"""
Hardcoded network + available security devices, used until the frontend/simulation layer
"""
from NW_Structure import NW_Node, NW_Sec_Device
from Simulation_Service import Simulation_Service


def sample_network():
    sim = Simulation_Service("sample")

    pc = NW_Node('PC', [10, 0, 0, 1], 1.0, 5.0, connections=[])
    laptop = NW_Node('Laptop', [10, 0, 0, 2], 1.0, 4.0, connections=[])
    switch = NW_Node('Switch', [10, 0, 0, 3], 2.0, 4.0, connections=[])
    router = NW_Node('Router', [10, 0, 0, 4], 2.0, 6.0, connections=[])
    server = NW_Node('Server', [10, 0, 0, 5], 1.0, 8.0, connections=[])

    def link(a, b, port):
        # both directions, since the solver treats links as directed
        a.add_connection(list(b.device_ip), 1, 10, 'TCP', port)
        b.add_connection(list(a.device_ip), 1, 10, 'TCP', port)

    link(pc, switch, 1000)
    link(laptop, switch, 1001)
    link(switch, router, 1002)
    link(router, server, 1003)

    for n in (pc, laptop, switch, router, server):
        sim.create_node(n)

    # device_type must currently be one of NW_Node.DEVICE_TYPES, so 'Router' stands in for a firewall/IDS
    sec_devices = [
        NW_Sec_Device('Router', [10, 1, 0, 1], 0.0, 0.0, 1.5, covered_devices=[], connections=[]),
        NW_Sec_Device('Router', [10, 1, 0, 2], 0.0, 0.0, 2.0, covered_devices=[], connections=[]),
    ]
    return sim, sec_devices