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

        :param device_type: str that states what type of network-connected device is represnted by this node
        :param device_ip: a 4-element list consisting of integers between 0 and 255 (inclusive), acting as a unique identifier
        :param base_sec_level: a float that acts as the default value for this node's security_level field
        :param risk_level: a float that acts as the target value that this node's security_level should be
        :param connections: a list of tuples that contain all info regarding a connection from this node to another node on the network
        """
        self.device_type = device_type
        self.device_ip = device_ip
        self.security_level = base_sec_level
        self.risk_level = risk_level
        self.connections = connections

class NW_Sec_Device(NW_Node):

    def __init__(self, device_type, device_ip, base_sec_level, risk_level, sec_modifier, covered_devices = [], connections = []):
        """
        :type device_type: str
        :type device_ip: list<int>
        :type base_sec_level: float
        :type risk_level: float
        :type sec_modifier: str
        :type covered_devices: list< tuple<NW_Node, ip:list<int>> >
        :type connections: list< tuple< NW_Node, ip:list<int>, cost:int, bandwidth:int, connection_type:str > >

        :param device_type: str that states what type of network-connected device is represented by this node
        :param device_ip: a 4-element list consisting of integers between 0 and 255 (inclusive), acting as a unique identifier
        :param base_sec_level: a float that acts as the default value for this node's security_level field
        :param risk_level: a float that acts as the target value that this node's security_level should be
        :param sec_modifier: a float value that is added to the security_level of all nodes covered by this security device
        :param covered_devices: a list of tuples that contain the memory address and ip address of another node covered by this security device
        :param connections: a list of tuples that contain all info regarding a connection from this node to another node on the network
        """
        NW_Node.__init__(self, device_type, device_ip, base_sec_level, risk_level, connections)
        self.sec_modifier = sec_modifier
        self.covered_devices = covered_devices

