import unittest
from src.simulation.Simulation_Service import Simulation_Service
from src.simulation.NW_Structure import *




class Simulation_Service_Test(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(True, True)  # add assertion here

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
                (00000000,), #constructor vals
                (node1,), #funciton args
                (Simulation_Service, 00000000, '', None, [node1]) #expected state vals afterwards
            ),
            ( #Test Case 2
                (99999999,), #constructor vals
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
            expected_object_type, expected_id, expected_state_str, expected_config, expected_node_list = expected_output
            new_object_1 = class_type(*inputs_1)

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
                (00000000,),  # constructor vals
                ('node1',),  # funciton args, needs to include at least one comma
                (TypeError)  # expected error details
            ),
            (  # Test Case 2
                (99999999,),  # constructor vals
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
            new_object_1 = class_type(*inputs_1)

            # perform functions to be tested
            with self.assertRaises(expected_error) as cm:
                function_var(new_object_1, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception,test_no))

    # Test the search_for_node method

    def test_Simulation_Service_search_for_node_state_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'search-for-node'
        function_var = class_type.search_for_node
        test_type = 'state'
        node1 = NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)
        node2 = NW_Node('Server', [1, 1, 1, 1], 1.0, 1.0)
        test_cases = [
            ( #Test Case 1
                (00000000,[node1]), #constructor vals
                ([0,0,0,0],), #funciton args
                (Simulation_Service, 00000000, '', None, [node1]) #expected state vals afterwards
            ),
            ( #Test Case 2
                (99999999,[node2]), #constructor vals
                ([1,1,1,1],), #funciton args
                (Simulation_Service, 99999999, '', None, [node2]) #expected state vals afterwards
            ),
            ( #Test Case 3
                (12345678,[node1]), #constructor vals
                ([1,1,1,1],), #funciton args
                (Simulation_Service, 12345678, '', None, [node1]) #expected state vals afterwards
            ),

        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            expected_object_type, expected_id, expected_state_str, expected_config, expected_node_list = expected_output
            new_object_1 = class_type(*inputs_1)

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

    def test_Simulation_Service_search_for_node_value_tests(self):
            # a test case is a set of two tuples - inputs, expected results
            class_type = Simulation_Service
            class_type_str = 'simulation-service'
            fpath_func = 'search-for-node'
            function_var = class_type.search_for_node
            test_type = 'value'
            node1 = NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)
            node2 = NW_Node('Server', [1, 1, 1, 1], 1.0, 1.0)
            test_cases = [
                ( #Test Case 1
                    (00000000,[node1]), #constructor vals
                    ([0,0,0,0],), #funciton args
                    (NW_Node, node1) #expected return vals afterwards
                ),
                ( #Test Case 2
                    (99999999,[node2]), #constructor vals
                    ([1,1,1,1],), #funciton args
                    (NW_Node, node2) #expected return vals afterwards
                ),
                ( #Test Case 3
                    (12345678,[node1]), #constructor vals
                    ([1,1,1,1],), #funciton args
                    (type(None),None) #expected return vals afterwards
                ),
            ]
            for test_case in test_cases:
                # test setup
                test_no = test_cases.index(test_case) + 1
                inputs_1 = test_case[0]
                func_args = test_case[1]
                expected_output_1 = test_case[2]
                expected_return_type, expected_return_value = expected_output_1
                new_stream_1 = class_type(*inputs_1)

                # perform functions to be tested

                result =  function_var(new_stream_1, *func_args)


                # assert that actual is expected
                self.assertEqual(expected_return_type, type(result),
                                 'Failed type checking of returned value | got: {}, expected: {} for test no. {}a'.format(
                                     type(result), expected_return_type, test_no))  # add assertion here
                self.assertEqual(expected_return_value, result,
                                 'Failed value checking of returned value | got: {}, expected: {} for test no. {}a'.format(
                                     result, expected_return_value, test_no))  # add assertion here

    # Test the connect_via_ip method
    def test_Simulation_Service_connect_via_ip_state_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'connect-via-ip'
        function_var = class_type.connect_via_ip
        test_type = 'state'
        node1 = NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)
        node2 = NW_Node('Server', [1, 1, 1, 1], 1.0, 1.0)
        node3 = NW_Node('Server', [2, 2, 2, 2], 2.0, 2.0)
        node4 = NW_Node('Server', [3, 3, 3, 3], 3.0, 3.0)
        node5 = NW_Node('Server', [4, 4, 4, 4], 4.0, 4.0)
        node6 = NW_Node('Server', [5, 5, 5, 5], 5.0, 5.0)
        test_cases = [
            ( #Test Case 1
                (00000000,[node1, node2]), #constructor vals
                ([0,0,0,0],80,[1,1,1,1],1,1,'TCP'), #funciton args
                (Simulation_Service, 00000000, '', None, [node1, node2]), #expected state vals afterwards
                [
                    (NW_Node, 'PC',[0,0,0,0],0.0,0.0,0.0,[([1,1,1,1],1,1,'TCP',80)]),
                    (NW_Node, 'Server',[1,1,1,1],1.0,1.0,1.0,[])
                ]
            ),
            ( #Test Case 2
                (99999999,[node3, node4]), #constructor vals
                ([3,3,3,3],83,[2,2,2,2],3,3,'TCP'), #funciton args
                (Simulation_Service, 99999999, '', None, [node3, node4]), #expected state vals afterwards
                [
                    (NW_Node, 'Server', [2, 2, 2, 2], 2.0, 2.0,2.0, []),
                    (NW_Node, 'Server', [3, 3, 3, 3], 3.0, 3.0, 3.0, [([2, 2, 2, 2], 3, 3, 'TCP', 83)])
                ]
            ),
            ( #Test Case 3
                (12345678,[node5, node6]), #constructor vals
                ([4,4,4,4],40,[4,4,4,4],4,4,'UDP'), #funciton args
                (Simulation_Service, 12345678, '', None, [node5, node6]), #expected state vals afterwards
                [
                    (NW_Node, 'Server', [4, 4, 4, 4], 4.0,4.0, 4.0, [([4, 4, 4, 4], 4, 4, 'UDP', 40)]),
                    (NW_Node, 'Server', [5, 5, 5, 5], 5.0,5.0, 5.0, [])
                ]
            ),

        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            expected_node_state_list = test_case[3]
            expected_object_type, expected_id, expected_state_str, expected_config, expected_node_list = expected_output
            new_object_1 = class_type(*inputs_1)

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

            for entry in expected_node_state_list:
                expected_node_data_type, expected_node_type,expected_node_ip, expected_node_base_sec_level, expected_node_cur_sec_level, expected_node_risk_level, expected_node_connections = entry
                act_node = new_object_1.search_for_node(expected_node_ip)
                print("act_node: ",act_node)
                self.assertEqual(expected_node_data_type, type(act_node),'Failed type checking of node | got: {}, expected: {} for test{} on entry {}'.format(type(act_node), expected_node_data_type, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_type, act_node.device_type,'Failed value checking of node_type | got: {}, expected: {} for test{} on entry {}'.format(act_node.device_type, expected_node_type, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_ip, act_node.device_ip,'Failed value checking of node_ip | got: {}, expected: {} for test{} on entry {}'.format(act_node.device_ip, expected_node_ip, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_base_sec_level, act_node.base_sec_level, 'Failed value checking of base_sec_level | got: {}, expected: {} for test{} on entry {}'.format(act_node.base_sec_level, expected_node_base_sec_level, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_cur_sec_level, act_node.security_level, 'Failed value checking of security_level | got: {}, expected: {} for test{} on entry {}'.format(act_node.security_level, expected_node_cur_sec_level, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_risk_level, act_node.risk_level, 'Failed value checking of risk_level | got: {}, expected: {} for test{} on entry {}'.format(act_node.risk_level, expected_node_risk_level, test_no,str(expected_node_state_list.index(entry)+1)))
                self.assertEqual(expected_node_connections, act_node.connections, 'Failed value checking of connections | got: {}, expected: {} for test{} on entry {}'.format(act_node.connections, expected_node_connections, test_no,str(expected_node_state_list.index(entry)+1)))

    # TESTS BELOW ARE CREATED WITH HELP OF GITHUB COPILOT (lines 340-438)
    def test_Simulation_Service_create_security_node_state_tests(self):
        security_node = NW_Sec_Device('Router', [10, 0, 0, 1], 1.0, 2.0, 0.5)
        simulation = Simulation_Service(123, [])

        simulation.create_security_node(security_node)

        self.assertEqual([security_node], simulation.node_list)
        self.assertIs(simulation.node_list[0], security_node)

    def test_Simulation_Service_create_security_node_error_tests(self):
        simulation = Simulation_Service(123, [])

        for invalid_node in ('node', NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)):
            with self.subTest(invalid_node=invalid_node):
                with self.assertRaises(TypeError):
                    simulation.create_security_node(invalid_node)

    def test_Simulation_Service_clear_nodes_state_tests(self):
        node = NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)
        nodes = [node]
        simulation = Simulation_Service(123, nodes)
        simulation.sim_state_str = 'previous state'

        simulation.clear_nodes()

        self.assertEqual([], simulation.node_list)
        self.assertIs(simulation.node_list, nodes)
        self.assertEqual('', simulation.sim_state_str)

    def test_Simulation_Service___del___state_tests(self):
        simulation = Simulation_Service(123, [NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)])
        simulation.sim_config = 'config'
        simulation.sim_state_str = 'previous state'

        simulation.__del__()

        self.assertEqual(-1, simulation.sim_id)
        self.assertIsNone(simulation.sim_config)
        self.assertEqual([], simulation.node_list)
        self.assertEqual('', simulation.sim_state_str)

    def test_Simulation_Service_get_sim_state_value_tests(self):
        node = NW_Node('PC', [1, 2, 3, 4], 0.0, 1.0)
        security_node = NW_Sec_Device('Router', [5, 6, 7, 8], 2.0, 3.0, 0.5)
        simulation = Simulation_Service(321, [node, security_node])
        simulation.sim_config = 'sample-config'

        self.assertEqual(
            '321#sample-config#[{};{}]'.format(
                node.get_state_str(), security_node.get_state_str()
            ),
            simulation.get_sim_state()
        )
        self.assertEqual('321#None#[]', Simulation_Service(321, []).get_sim_state())

    def test_Simulation_Service_connect_via_ip_missing_node_error_tests(self):
        source_ip = [0, 0, 0, 0]
        destination_ip = [1, 1, 1, 1]
        node = NW_Node('PC', source_ip, 0.0, 0.0)

        with self.subTest(missing='source'):
            simulation = Simulation_Service(1, [node])
            with self.assertRaises(IndexError):
                simulation.connect_via_ip([2, 2, 2, 2], 80, destination_ip)

        with self.subTest(missing='destination'):
            simulation = Simulation_Service(1, [node])
            with self.assertRaises(IndexError):
                simulation.connect_via_ip(source_ip, 80, destination_ip)

    def test_Simulation_Service_connect_via_ip_default_arguments_tests(self):
        source_ip = [0, 0, 0, 0]
        destination_ip = [1, 1, 1, 1]
        source = NW_Node('PC', source_ip, 0.0, 0.0)
        destination = NW_Node('Server', destination_ip, 0.0, 0.0)
        simulation = Simulation_Service(1, [source, destination])

        simulation.connect_via_ip(source_ip, 80, destination_ip)

        self.assertEqual([(destination_ip, 1, 1, 'TCP', 80)], source.connections)
        self.assertEqual([], destination.connections)

    def test_Simulation_Service_update_sim_error_test(self):
        with self.assertRaises(TypeError):
            Simulation_Service(1, []).update_sim()

    def test_Simulation_Service_extract_from_state_string_error_tests(self):
        simulation = Simulation_Service(1, [])

        with self.assertRaises(TypeError):
            simulation.extract_from_state_string(None)

        with self.assertRaises(ValueError):
            simulation.extract_from_state_string('1#config')

        with self.assertRaises(ValueError):
            simulation.extract_from_state_string('1#config#[invalid]')

        for malformed_state in (
            'not-numeric#config#[]',
            '1#config#[PC%[1&2&3]%0.0%0.0%0.0%[]]',
            '1#config#[PC%[1&2&3&4]%0.0%0.0%0.0%[([1=2=3]@1@1@TCP@80)]]',
        ):
            with self.subTest(state=malformed_state):
                with self.assertRaises(ValueError):
                    simulation.extract_from_state_string(malformed_state)

    def test_Simulation_Service_extract_from_state_string_error_preserves_state_test(self):
        node = NW_Node('PC', [0, 0, 0, 0], 0.0, 0.0)
        simulation = Simulation_Service(1, [node])
        simulation.sim_config = 'existing-config'
        simulation.sim_state_str = 'existing-state'

        with self.assertRaises(ValueError):
            simulation.extract_from_state_string('2#new-config#[invalid]')

        self.assertEqual(1, simulation.sim_id)
        self.assertEqual([node], simulation.node_list)
        self.assertEqual('existing-config', simulation.sim_config)
        self.assertEqual('existing-state', simulation.sim_state_str)

    def test_Simulation_Service_extract_from_state_string_empty_state_tests(self):
        state = '123#config#[]'
        simulation = Simulation_Service(0, [])

        simulation.extract_from_state_string(state)

        self.assertEqual(123, simulation.sim_id)
        self.assertEqual('config', simulation.sim_config)
        self.assertEqual([], simulation.node_list)
        self.assertEqual(state, simulation.sim_state_str)

    def test_Simulation_Service_extract_from_state_string_round_trip_tests(self):
        connection = ([9, 8, 7, 6], 4, 5, 'UDP', 1234)
        second_connection = ([8, 7, 6, 5], 6, 7, 'TCP', 4321)
        node = NW_Node(
            'PC', [1, 2, 3, 4], 0.5, 1.5,
            [connection, second_connection], current_security_level=0.75
        )
        security_node = NW_Sec_Device(
            'Router', [5, 6, 7, 8], 2.0, 3.0, 0.25,
            [[1, 2, 3, 4], [4, 3, 2, 1]],
            [connection, second_connection], current_security_level=2.5
        )
        original = Simulation_Service(456, [node, security_node])
        original.sim_config = 'config/path'
        state = original.get_sim_state()
        restored = Simulation_Service(0, [])

        restored.extract_from_state_string(state)

        self.assertEqual(state, restored.sim_state_str)
        self.assertEqual(456, restored.sim_id)
        self.assertEqual('config/path', restored.sim_config)
        self.assertEqual(2, len(restored.node_list))
        self.assertIs(type(restored.node_list[0]), NW_Node)
        self.assertEqual(node.device_ip, restored.node_list[0].device_ip)
        self.assertEqual(node.security_level, restored.node_list[0].security_level)
        self.assertEqual([connection, second_connection], restored.node_list[0].connections)
        self.assertIs(type(restored.node_list[1]), NW_Sec_Device)
        self.assertEqual(security_node.sec_modifier, restored.node_list[1].sec_modifier)
        self.assertEqual(security_node.covered_devices, restored.node_list[1].covered_devices)
        self.assertEqual(
            [connection, second_connection], restored.node_list[1].connections
        )
    #END OF AI-ASSISTED CODE

if __name__ == '__main__':
    unittest.main()
