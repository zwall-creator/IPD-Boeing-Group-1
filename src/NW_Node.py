"""
@version: v0.6
@team: Boeing Group 1
@contributors: [Zak Wallace]
"""

class NW_Node:

    def __init__(self, device_type, device_ip, base_sec_level, risk_level, connections = []):
        """
        :type device_type: str
        :type device_ip: list<int>
        :type base_sec_level: float
        :type risk_level: float
        :type connections: list< tuple< NW_Node, ip:list<int>, cost:int, bandwidth:int, connection_type:str > >
        """
        self.device_type = device_type
        self.device_ip = device_ip
        self.base_sec_level = base_sec_level
        self.risk_level = risk_level
        self.connections = connections
