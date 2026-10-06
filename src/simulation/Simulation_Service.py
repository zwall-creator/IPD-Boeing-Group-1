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
        if type(new_node) == NW_Node:
            self.node_list.append(new_node)

    def update_sim(self):
        #TODO: Implement functions to gather all sim information and store in sim_state_str
        raise NotImplemented

    def get_sim_state(self):
        state = ''
        for node in self.node_list:
            state += node.get_state_str()

        return state
