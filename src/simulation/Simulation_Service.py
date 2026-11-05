"""
@version: v0.8
@team: Boeing Group 1
@contributors: [Zak Wallace]
"""
from src.simulation.NW_Structure import *
class Simulation_Service:
    """
    Class to manage the service operations of a single simulation.
    Simulation_Service uses an Observer structure: updates occur when prompted by other classes

    """
    def __init__(self, sim_id):
        self.sim_id = sim_id
        self.sim_state_str = ''
        self.sim_config = None
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
            #TODO: UPDATE SIMULATION STATE STRING AFTER MODIFICATION
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
        #TODO: UPDATE SIMULATION STATE STR AFTER MODIFICATION

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
        '01234567#../data/configs/01234567config.txt#[PC,[255,255,255,255],0.0,1.0,2.0,[([0,0,0,0],1,1,TCP),([1,1,1,1],2,2,UDP)];Server,[0,0,0,0],0.0,0.0,3.0,[([255,255,255,255],30,45,UDP)];]'
        :return: a string instance of the simulation's state string
        """
        # TODO: Add implementation to replace any NONE or NULL values with null character ('\0')
        state = ''
        state += str(self.sim_id) + '#'
        state += str(self.sim_config_fpath) + '#['

        for i in range(len(self.node_list)):
            node = self.node_list[i]
            state += node.get_state_str()
            if i != len(self.node_list) - 1:
                state += ';'
        state += ']'
        return state

    def extract_from_state_string(self, state_string):
        """
        Function to extract data from a given state string and update the simulation service object with the extracted data
        \nNOTE: this will replace the current data for this simulation, so any unsaved changes will be lost!
        :param state_string: string instance of a simulation's state string
        """

        if type(state_string) != str:
            raise TypeError('state_string must be a string')

        # Split at syntax level 1
        sim_id, config, node_list = state_string.split('#')
        if sim_id.isnumeric():
            sim_id = int(sim_id)
            self.sim_id = sim_id
            # TODO: update self.sim_id with extracted id

        #TODO: Implement Config support

        #collect formatted data for this sim's nodes
        ret_nodes = []
        # Split at syntax level 2 for node_list
        node_list = node_list.split(';')
        for node_entry in node_list:

            #TODO: Implement boolean logic to extract NW_Node and NW_Sec_Device uniquely
            object_class = NW_Node

            # Split at syntax level 3 for node data
            device_type,device_ip_list,base_sec_level,security_level,risk_level,connections = node_entry.split('%')
            base_sec_level = float(base_sec_level)
            security_level = float(security_level)
            risk_level = float(risk_level)

            # Split at syntax level 4 for node IP address
            device_ip_list = device_ip_list.split('&')
            device_ip = [int(device_ip_list[0]), int(device_ip_list[1]), int(device_ip_list[2]), int(device_ip_list[3])]

            #collect formated data for this node's connections
            ret_connections = []
            # Split at syntax level 4 for node connections
            for connection_entry in connections.split('&'):

                # Split at syntax level 5 for connection details
                connection_ip_list,cost,bandwidth,connection_type,source_port = connection_entry.split('@')
                cost = int(cost)
                bandwidth = int(bandwidth)
                source_port = int(source_port)

                # Split at syntax level 6 for connection's destination IP address
                connection_ip_list = connection_ip_list.split('=')
                connection_ip = [int(connection_ip_list[0]), int(connection_ip_list[1]), int(connection_ip_list[2]), int(connection_ip_list[3])]

                ret_connections.append((connection_ip,cost,bandwidth,connection_type,source_port))
            constructor_args = (device_type,device_ip,base_sec_level,risk_level,ret_connections, security_level)
            ret_nodes.append(object_class(*constructor_args))
        self.node_list = ret_nodes
        self.sim_config_fpath = config
        new_state_str = self.get_sim_state()
        if new_state_str != state_string:
            raise ValueError('New simulation state string\n{}\n does not match the given state string\n{}\n'.format(new_state_str,state_string))
        self.sim_state_str = new_state_str