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
