"""
@version: v0.7
@team: Boeing Group 1
@contributors: [Zak Wallace]
"""
from NW_Structure import *
class Simulation_Service:
    """
    Class to manage the service operations of a single simulation.
    Simulation_Service uses an Observer structure: updates occur when prompted by other classes

    """
    def __init__(self, sim_id, sim_state_str = '', sim_config_fpath = None):
        self.sim_id = sim_id
        self.sim_state_str = sim_state_str
        self.sim_config_fpath = sim_config_fpath
        self.node_list = []

    def create_node(self, new_node):
        """
        Given a NW_Node object, add that node to the simulation
        :type new_node: NW_Node

        :param new_node: NW_Node object to add to simulation
        :return: True if successful, False otherwise
        :raises: TypeError
        """
        if type(new_node) == NW_Node:
            self.node_list.append(new_node)
        else:
            raise TypeError('new_node must be a NW_Node object')

    def search_for_node(self, node_ip):
        """
        Searches for the first instance of a NW_Node object in the simulation with the given IP address
        :type node_ip: list<int>
        :param node_ip: unique identifier to search for
        :return: NW_Node object if present in simulation, None otherwise
        """
        for node in self.node_list:
            if node.device_ip == node_ip:
                return node
        return None

    def connect_via_ip(self, source_ip, destination_ip, cost = 1, bandwidth = 1, connection_type = 'TCP'):
        """
        Function to create a new one-way connection between THIS NW_Node and another node on the network. Destination target node is determined by the given IP address (destination_ip)
        :type source_ip: list<int>
        :type destination_ip: list<int>
        :type cost: int
        :type bandwidth: int
        :type connection_type: str

        :param source_ip: List of four integer values (0..255) that indicate a unique identifier for the source node
        :param destination_ip: List of four integer values (0..255, inclusive) that indicate a unique identifier for the target node
        :param cost: cost for sending data across this connection
        :param bandwidth: maximum number of cost units that this connection can handle
        :param connection_type: the type of protocol used for this connection
        :return: True if connection was successful, False otherwise
        :raises: TypeError if source_ip and destination_ip do not exist in the simulation
        """
        #search the network for Nodes with given IP addresses
        src_node = self.search_for_node(source_ip)
        dest_node = self.search_for_node(destination_ip)
        #if a given IP address is not present in the simulation, throw IndexErrors
        if src_node is None:
            raise IndexError('No NW_Node found in this simulation with ip address: {}'.format(source_ip))
        if dest_node is None:
            raise IndexError('No NW_Node found in this simulation with ip address: {}'.format(destination_ip))
        #create the connection between the two nodes
        src_node.add_connection(dest_node, cost, bandwidth, connection_type)

    def update_sim(self):
        """
        Function to prompt Simulation_Service to update the simulation state. Usually called by other classes when information is modified.
        :return: True if successful changes were updated, False if failed to update or no changes were found
        """
        #TODO: Implement functions to gather all sim information and store in sim_state_str
        raise NotImplemented

    def get_sim_state(self):
        """
        Function to get the state string of the entire simulation.
        \n example of state string syntax: \n
        '01234567,../data/configs/01234567config.txt,[PC,255.255.255.255,0.0,1.0,2.0,[(0.0.0.0,1,1,TCP),(1.1.1.1,2,2,UDP);Server,0.0.0.0,0.0,0.0,3.0,[(255.255.255.255,30,45,UDP)];]'
        :return: a string instance of the simulation's state string
        """
        # TODO: Add implementation to replace any NONE or NULL values with null character ('\0')
        state = ''
        state += str(self.sim_id) + ','
        state += str(self.sim_config_fpath) + ',['
        for node in self.node_list:
            state += node.get_state_str()
        state += ']'
        return state

    def extract_from_state_string(self, state_string):
        """
        Function to extract data from a given state string and update the simulation service object with the extracted data
        \nNOTE: this will replace the current data for this simulation, so any unsaved changes will be lost!
        :param state_string: string instance of a simulation's state string
        """
        raise NotImplemented