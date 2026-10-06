"""
@version: v0.6
@team: Boeing Group 1
@contributors: [Zak Wallace]
"""
from typing import override


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

    def __str__(self):
        """
        Creates a user-readable string representation of this NW_Node
        \n NOTE: not to be confused with get_state_str()
        :return: a string representation of this NW_Node
        """
        retstr = 'device_type: {}, device_ip: {}, security_level: {}, risk_level: {}, self.connections: {}'.format(self.device_type, self.device_ip, self.security_level, self.risk_level, self.connections)
        return retstr

    def __gt__(self, other):
        """
        :type other: NW_Node
        :param other: Another NW_Node instance object to compare against this one
        :return: True if THIS NW_Node has a greater security_level than given NW_Node. Returns False otherwise.
        """
        if type(other) == NW_Node:
            if self.security_level > other.security_level:
                return True
        return False

    def __eq__(self, other):
        """
        :type other: NW_Node
        :param other: Another NW_Node instance object to compare against this one
        :return: True if THIS NW_Node has a equal security_level than given NW_Node. Returns False otherwise.
        """
        if type(other) == NW_Node:
            if self.security_level == other.security_level:
                return True
        return False



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

    @override
    def __str__(self):
        """
        Creates a user-readable string representation of this NW_Sec_Device
        :return: a string representation of this NW_Sec_Device
        """
        retstr = super().__str__() + ', sec_modifier: {}, covered_devices: {}'.format(self.sec_modifier, self.covered_devices)
        return retstr


