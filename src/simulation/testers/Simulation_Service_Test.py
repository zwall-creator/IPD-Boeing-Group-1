import unittest
from src.simulation.Simulation_Service import Simulation_Service
from src.simulation.NW_Structure import *


class Simulation_Service_Test(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    # Test the __init__ method
    def test_Simulation_Service__init__state_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'init'
        # function_var = class_type.__str__
        test_type = 'state'
        test_cases = [
            ( #Test Case 1
                (00000000), #constructor vals
                (), #funciton args
                (Simulation_Service, 00000000, '', None, []) #expected state vals afterwards
            ),
            ( #Test Case 2
                (99999999), #constructor vals
                (), #funciton args
                (Simulation_Service, 99999999, '', None, []) #expected state vals afterwards
            ),
        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            id = inputs_1
            expected_object_type, expected_id, expected_state_str, expected_config, expected_node_list = expected_output
            new_object_1 = class_type(id)

            # perform functions to be tested
            # result = function_var(new_object_1, *func_args)

            # assert that actual is expected
            self.assertEqual(expected_object_type, type(new_object_1),
                             'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(
                                 type(new_object_1), expected_object_type, test_no))  # add assertion here
            self.assertEqual(expected_id, new_object_1.sim_id,
                             'Failed value checking of sim_id | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_id, expected_id, test_no))  # add assertion here
            self.assertEqual(expected_state_str, new_object_1.sim_state_str,
                             'Failed value checking of sim_state_str | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_state_str, expected_state_str, test_no))  # add assertion here
            self.assertEqual(expected_config, new_object_1.sim_config,
                             'Failed value checking of sim_config | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_config, expected_config, test_no))  # add assertion here
            self.assertEqual(expected_node_list, new_object_1.node_list,
                             'Failed value checking of node_list | got: {}, expected: {} for test{}'.format(
                                 new_object_1.node_list, expected_node_list, test_no))  # add assertion here

    # Test the create_node method
    def test_Simulation_Service_create_node_state_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'create_node'
        function_var = class_type.create_node
        test_type = 'state'
        node1 =NW_Node('PC',[0,0,0,0],0.0,0.0)
        node2 =NW_Node('Server',[1,1,1,1],1.0,1.0)
        test_cases = [
            ( #Test Case 1
                (00000000), #constructor vals
                (node1,), #funciton args
                (Simulation_Service, 00000000, '', None, [node1]) #expected state vals afterwards
            ),
            ( #Test Case 2
                (99999999), #constructor vals
                (node2,), #funciton args
                (Simulation_Service, 99999999, '', None, [node2]) #expected state vals afterwards
            ),
        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            id = inputs_1
            expected_object_type, expected_id, expected_state_str, expected_config, expected_node_list = expected_output
            new_object_1 = class_type(id)

            # perform functions to be tested
            result = function_var(new_object_1, *func_args)

            # assert that actual is expected
            self.assertEqual(expected_object_type, type(new_object_1),
                             'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(
                                 type(new_object_1), expected_object_type, test_no))  # add assertion here
            self.assertEqual(expected_id, new_object_1.sim_id,
                             'Failed value checking of sim_id | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_id, expected_id, test_no))  # add assertion here
            self.assertEqual(expected_state_str, new_object_1.sim_state_str,
                             'Failed value checking of sim_state_str | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_state_str, expected_state_str, test_no))  # add assertion here
            self.assertEqual(expected_config, new_object_1.sim_config,
                             'Failed value checking of sim_config | got: {}, expected: {} for test{}'.format(
                                 new_object_1.sim_config, expected_config, test_no))  # add assertion here
            self.assertEqual(expected_node_list, new_object_1.node_list,
                             'Failed value checking of node_list | got: {}, expected: {} for test{}'.format(
                                 new_object_1.node_list, expected_node_list, test_no))  # add assertion here

    def test_Simulation_Service_create_node_error_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'create-node'
        function_var = class_type.create_node
        test_type = 'error'
        test_cases = [
            (  # Test Case 1
                (00000000),  # constructor vals
                ('node1',),  # funciton args, needs to include at least one comma
                (TypeError)  # expected error details
            ),
            (  # Test Case 2
                (99999999),  # constructor vals
                (1,),  # funciton args, needs to include at least one comma
                (TypeError)  # expected state vals afterwards
            ),
        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            id = inputs_1
            expected_error = expected_output
            new_object_1 = class_type(id)

            # perform functions to be tested
            with self.assertRaises(expected_error) as cm:
                function_var(new_object_1, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception,test_no))



if __name__ == '__main__':
    unittest.main()
