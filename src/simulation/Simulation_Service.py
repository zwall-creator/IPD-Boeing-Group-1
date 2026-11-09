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
    def __init__(self, sim_id, node_list = None):
        self.sim_id = sim_id
        self.sim_state_str = ''
        self.sim_config = None
        self.node_list = [] if node_list == None else node_list

    def __del__(self):
        self.sim_id = -1
        self.sim_config = None
        self.clear_nodes()

    def clear_nodes(self):
        self.node_list.clear()
        self.sim_state_str = ''


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

    def create_security_node(self, new_node):
        """
        Given a NW_Sec_Device object, add that node to the simulation
        :type new_node: NW_Node

        :param new_node: NW_Sec_Device object to add to simulation
        :return: True if successful, False otherwise
        :raises: TypeError
        """
        if type(new_node) == NW_Sec_Device:
            self.node_list.append(new_node)
            #TODO: UPDATE SIMULATION STATE STRING AFTER MODIFICATION
        else:
            raise TypeError('new_node must be a NW_Sec_Device object')

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

    def connect_via_ip(self, source_ip, src_port, destination_ip, cost = 1, bandwidth = 1, connection_type = 'TCP'):
        """
        Function to create a new one-way connection between THIS NW_Node and another node on the network. Destination target node is determined by the given IP address (destination_ip)
        :type src_port: int
        :type source_ip: list<int>
        :type destination_ip: list<int>
        :type cost: int
        :type bandwidth: int
        :type connection_type: str

        :param src_port: source port number
        :param source_ip: List of four integer values (0..255) that indicate a unique identifier for the source node
        :param destination_ip: List of four integer values (0..255, inclusive) that indicate a unique identifier for the target node
        :param cost: cost for sending data across this connection
        :param bandwidth: maximum number of cost units that this connection can handle
        :param connection_type: the type of protocol used for this connection
        :return: True if connection was successful, False otherwise
        :raises: TypeError if source_ip and destination_ip do not exist in the simulation
        """
        #search the network for Nodes with given IP addresses
        print(source_ip)
        print(destination_ip)
        src_node = self.search_for_node(source_ip)
        dest_node = self.search_for_node(destination_ip)
        #if a given IP address is not present in the simulation, throw IndexErrors
        if src_node is None:
            raise IndexError('No NW_Node found in this simulation with ip address: {}'.format(source_ip))
        if dest_node is None:
            raise IndexError('No NW_Node found in this simulation with ip address: {}'.format(destination_ip))
        #create the connection between the two nodes

        print(src_node)
        print(dest_node)
        dest_node = None
        print(src_node)
        print(dest_node)
        src_node.add_connection(destination_ip, cost, bandwidth, connection_type, src_port)
        print(src_node)
        print(dest_node)
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
        state += str(self.sim_config) + '#['

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
        \nNote: at 11/8/2026 at 1:04 PM, The following lines were modified with GitHub Copilot to resolve errors: 152,164,170,178-179,190-191,193-203,208-209,212,216-220,229-231,234-236
        """
        if type(state_string) != str:
            raise TypeError('state_string must be a string')

        # Split at syntax level 1
        sim_id, config, node_list = state_string.split('#')
        if node_list[0] == '[' and node_list[-1] == ']':
            node_list = node_list[1:-1]
        if sim_id.isnumeric():
            sim_id = int(sim_id)
        else:
            raise ValueError('sim_id must be an integer')
            # TODO: update self.sim_id with extracted id

        #TODO: Implement Config support

        #collect formatted data for this sim's nodes
        ret_nodes = []
        # Split at syntax level 2 for node_list
        if node_list:
            node_list = node_list.split(';')
        else:
            node_list = []
        for node_entry in node_list:
            # Split at syntax level 3 for node data
            #Implement boolean logic to extract NW_Node and NW_Sec_Device uniquely
            node_data = node_entry.split('%')
            object_class = object
            device_type, device_ip_list, base_sec_level, security_level, risk_level, sec_modifier, covered_devices, connections = 'INVALID', [], -99.0, -99.0, -99.0, None, None, []
            if len(node_data) == 6:
                object_class = NW_Node
                device_type, device_ip_list, base_sec_level, security_level, risk_level, connections = node_data
            elif len(node_data) == 8:
                object_class = NW_Sec_Device
                device_type, device_ip_list, base_sec_level, security_level, risk_level, sec_modifier, covered_devices, connections = node_data
                sec_modifier = float(sec_modifier)
            else:
                raise ValueError('Node state must contain 6 or 8 fields')




            base_sec_level = float(base_sec_level)
            security_level = float(security_level)
            risk_level = float(risk_level)

            # Split at syntax level 4 for node IP address and coverages
            device_ip_list = device_ip_list[1:-1].split('&')
            if len(device_ip_list) != 4:
                raise ValueError('Node IP address must contain 4 bytes')
            device_ip = [int(device_ip_list[0]), int(device_ip_list[1]), int(device_ip_list[2]), int(device_ip_list[3])]
            covered_device_ips = None
            if covered_devices is not None:
                covered_device_ips = []
                coverage_data = covered_devices[1:-1]
                for coverage_entry in coverage_data.split('&') if coverage_data else []:
                    #split at syntax level 5 for individual ips that are covered
                    coverage_entry = coverage_entry.strip('[]').split('@')
                    if len(coverage_entry) != 4:
                        raise ValueError('Covered device IP address must contain 4 bytes')
                    covered_ip = [int(coverage_entry[0]), int(coverage_entry[1]), int(coverage_entry[2]), int(coverage_entry[3])]
                    covered_device_ips.append(covered_ip)

            #collect formated data for this node's connections
            ret_connections = []
            # Split at syntax level 4 for node connections
            connection_data = connections[1:-1]
            for connection_entry in connection_data.split('&') if connection_data else []:

                # Split at syntax level 5 for connection details
                connection_ip_list,cost,bandwidth,connection_type,source_port = connection_entry.strip('()').split('@')
                cost = int(cost)
                bandwidth = int(bandwidth)
                source_port = int(source_port)

                # Split at syntax level 6 for connection's destination IP address
                connection_ip_list = connection_ip_list.strip('[]').split('=')
                if len(connection_ip_list) != 4:
                    raise ValueError('Connection IP address must contain 4 bytes')
                connection_ip = [int(connection_ip_list[0]), int(connection_ip_list[1]), int(connection_ip_list[2]), int(connection_ip_list[3])]

                ret_connections.append((connection_ip,cost,bandwidth,connection_type,source_port))
            constructor_args = [device_type,device_ip,base_sec_level,risk_level,ret_connections, security_level]
            if covered_device_ips is not None and sec_modifier is not None:
                constructor_args = [device_type,device_ip,base_sec_level,risk_level,sec_modifier,covered_device_ips,ret_connections, security_level]

            ret_nodes.append(object_class(*constructor_args))
        new_state_str = '{}#{}#[{}]'.format(
            sim_id, config, ';'.join(node.get_state_str() for node in ret_nodes)
        )
        if new_state_str != state_string:
            raise ValueError('New simulation state string\n{}\n does not match the given state string\n{}\n'.format(new_state_str,state_string))
        self.sim_id = sim_id
        self.node_list = ret_nodes
        self.sim_config = config
        self.sim_state_str = new_state_str