import unittest

from src.simulation.NW_Structure import NW_Node, NW_Sec_Device

#Template for parameters for constructor tests (does not include current security_level value)
TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES = {
        'Empty PC Node': ('PC',[0,0,0,0],0.0,0.0,[]),
        'Empty Mobile Node': ('Mobile',[0,0,0,0],0.0,0.0,[]),
        'Empty Server Node': ('Server',[0,0,0,0],0.0,0.0,[]),
        'Invalid IP Node': ('PC',[256,256,256,256],0.0,0.0,[]),
        'Negative IP Node': ('PC',[-1,-1,-1,-1],0.0,0.0,[]),
        'None Type Node': (None,None,None,None),
        'Single TCP Connection PC Node' : ('PC',[0,0,0,0],0.0,0.0,[([1,1,1,1],1,1,'TCP',80)])
}
#Template for parameters for constructor tests (includes current security_level values)
TEMPLATE_NODE_TEST_STATES = {
    'Empty PC Node': ('PC', [0, 0, 0, 0], 0.0, 0.0, 0.0, []),
    'Empty Mobile Node': ('Mobile', [0, 0, 0, 0], 0.0, 0.0, 0.0, []),
    'Empty Server Node': ('Server', [0, 0, 0, 0], 0.0, 0.0, 0.0, []),
    'Invalid IP Node': ('PC', [256, 256, 256, 256], 0.0, 0.0, 0.0, []),
    'Negative IP Node': ('PC', [-1, -1, -1, -1], 0.0, 0.0, 0.0, []),
    'None Type Node': (None, None, None, None, None),
}
#This template must have only valid nodes (cannot construct erroneous nodes)
TEMPLATE_NODE_OBJECTS = {
    'Empty PC Node': NW_Node('PC',[0,0,0,0],0.0,0.0,[]),
    'Empty Mobile Node': NW_Node('Mobile',[0,0,0,0],0.0,0.0,[]),
    'Empty Server Node': NW_Node('Server',[0,0,0,0],0.0,0.0,[]),
}
class NW_Structure_Test(unittest.TestCase):

# Control tests; these should NEVER fail
    def test_pass(self):
        self.assertEqual(True, True)  # add assertion here
    def test_fail(self):
        self.assertNotEqual(True, False)  # add assertion here

# Tests for NW_Node's __init__ function
    def test_NW_Node__init__state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node = NW_Node(device_type, ip, base_sec_level, risk_level, connections)
            self.assertEqual(type(new_node), expected_object_type, 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node),expected_object_type)) # add assertion here
            self.assertEqual(new_node.device_type, expected_device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node.device_type,expected_device_type))  # add assertion here
            self.assertEqual(new_node.device_ip, expected_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node.device_ip,expected_ip))  # add assertion here
            self.assertEqual(new_node.base_sec_level, expected_base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(new_node.security_level, expected_security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node.security_level,expected_security_level))  # add assertion here
            self.assertEqual(new_node.risk_level, expected_risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(new_node.connections, expected_connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node.connections,expected_connections))  # add assertion here

    def test_NW_Node__init__error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[256,0,0,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,256,0,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,0,256,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,0,0,256],0.0,0.0,[]),(ValueError)),
            (('PC',[-1,0,0,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,-1,0,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,0,-1,0],0.0,0.0,[]),(ValueError)),
            (('PC',[0,0,0,-1],0.0,0.0,[]),(ValueError)),
            (('PC',[0,0,0,0],0.0,0.0,()),(TypeError)),
            (('PC',[0,0,0,0],0.0,0.0,'Not a List'),(TypeError)),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                NW_Node(device_type, ip, base_sec_level, risk_level, connections)
            actual_exception = cm.exception
            self.assertEqual(type(actual_exception), expected_error, 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))


    def test_NW_Node__init__NONE_value_errors(self):
        """
        Test function to ensure that __init__ function for NW_Node handles incorrect input types
        :return:
        """
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((None,[0,0,0,0],0.0,0.0,[]),(TypeError)),
            (('PC',None,0.0,0.0,[]),(TypeError)),
            (('PC',[None,0,0,0],0.0,0.0,[]),(TypeError)),
            (('PC',[0,None,0,0],0.0,0.0,[]),(TypeError)),
            (('PC',[0,0,None,0],0.0,0.0,[]),(TypeError)),
            (('PC',[0,0,0,None],0.0,0.0,[]),(TypeError)),
            (('PC',[0,0,0,0],None,0.0,[]),(TypeError)),
            (('PC',[0,0,0,0],0.0,None,[]),(TypeError)),
            (('PC',[0.1,0,0,0],0.0,0.0,[]),(TypeError)),
            ((1,[0,0,0,0],0.0,0.0,[]),(TypeError)),
            (('PC',1,0.0,0.0,[]),(TypeError)),
            (('PC','0.0.0.0',0.0,0.0,[]),(TypeError)),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                NW_Node(device_type, ip, base_sec_level, risk_level, connections)
            actual_exception = cm.exception
            self.assertEqual(type(actual_exception), expected_error, 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))

# Tests for NW_Node's __str__ function
    def test_NW_Node__str__state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node = NW_Node(device_type, ip, base_sec_level, risk_level, connections)

            #run function to be tested
            result = str(new_node)

            #assert state is now as expected
            self.assertEqual(expected_object_type, type(new_node), 'Failed type checking of object | got: {}, expected: {}'.format(type(new_node),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node.connections,expected_connections))  # add assertion here

    def test_NW_Node__str__value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(str,'PC,[0,0,0,0],0.0,0.0,0.0,[]')),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(str,'Mobile,[0,0,0,0],0.0,0.0,0.0,[]')),
        ]
        for test_case in test_cases:
            #test setup
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_return_type, expected_return_value = expected_output
            new_node = NW_Node(device_type, ip, base_sec_level, risk_level, connections)

            #run function to be tested
            result = str(new_node)

            #assert state is now as expected
            self.assertEqual(expected_return_type, type(result), 'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_type, type(result), 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

# Tests for NW_Node's __gt__ function
    def test_NW_Node__gt__state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2 = inputs_2
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = NW_Node(device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2)

            #perform functions to be tested
            new_node_1.__gt__(new_node_2)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node__gt__value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty PC Node'], (bool, False)),
            (('PC',[0,0,0,0],1.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty PC Node'], (bool, True)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('Mobile',[0,0,0,0],1.0,0.0,[]),(bool,False)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],1.0,0.0,[]),(bool,False)),
            (('Mobile',[0,0,0,0],1.0,0.0,None),('Mobile',[0,0,0,0],0.0,0.0,[]),(bool,True)),
            (('Mobile',[0,0,0,0],0.0,0.0,None),('Mobile',[0,0,0,0],1.0,0.0,[]),(bool,False)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2 = inputs_2
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = NW_Node(device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2)

            #perform functions to be tested
            result = new_node_1.__gt__(new_node_2)

            #assert that actual is expected
            self.assertEqual(expected_return_type, type(result), 'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    def test_NW_Node__gt__errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), None, (TypeError)),
            (('PC',[0,0,0,0],1.0,0.0,[]), 'string instance', (TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0.0,(TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0,(TypeError)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            node_2 = inputs_2
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = node_2


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.__gt__(new_node_2)
            actual_exception = cm.exception
            self.assertEqual(expected_error,type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's __eq__ function
    def test_NW_Node__eq__state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2 = inputs_2
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = NW_Node(device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2)

            #perform functions to be tested
            new_node_1.__eq__(new_node_2)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual( expected_device_type, new_node_1.device_type,'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node__eq__value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty PC Node'], (bool, True)),
            (('PC',[0,0,0,0],1.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty PC Node'], (bool, False)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty PC Node'], (bool, True)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]), TEMPLATE_NODE_CONSTRUCTOR_TEST_STATES['Empty Mobile Node'], (bool, True)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('Mobile',[0,0,0,0],1.0,0.0,[]),(bool,False)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),('PC',[0,0,0,0],1.0,0.0,[]),(bool,False)),
            (('Mobile',[0,0,0,0],1.0,0.0,None),('Mobile',[0,0,0,0],0.0,0.0,[]),(bool,False)),
            (('Mobile',[0,0,0,0],0.0,0.0,None),('Mobile',[0,0,0,0],1.0,0.0,[]),(bool,False)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2 = inputs_2
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = NW_Node(device_type_2, ip_2, base_sec_level_2, risk_level_2, connections_2)

            #perform functions to be tested
            result = new_node_1.__eq__(new_node_2)

            #assert that actual is expected
            self.assertEqual(expected_return_type, type(result), 'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    def test_NW_Node__eq__errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), None, (TypeError)),
            (('PC',[0,0,0,0],1.0,0.0,[]), 'string instance', (TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0.0,(TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0,(TypeError)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            inputs_2 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            node_2 = inputs_2
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)
            new_node_2 = node_2


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.__eq__(new_node_2)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's get_state_str function
    def test_NW_Node_get_state_str_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80),])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            expected_output = test_case[1]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.get_state_str()

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node_get_state_str_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), (str, 'PC,[0,0,0,0],0.0,0.0,0.0,[];')),
            (('PC',[0,0,0,0],1.0,0.0,[]), (str, 'PC,[0,0,0,0],1.0,1.0,0.0,[];')),
            (('Mobile',[0,0,0,0],0.0,0.0,[]), (str, 'Mobile,[0,0,0,0],0.0,0.0,0.0,[];')),
            (('Mobile',[0,0,0,0],1.0,0.0,None),(str,'Mobile,[0,0,0,0],1.0,1.0,0.0,[];')),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(str,'Mobile,[0,0,0,0],0.0,0.0,0.0,[];')),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),]),(str,'Mobile,[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,TCP,80)];')),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),(str,'Mobile,[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,TCP,80),([0,0,0,2],3,4,UDP,81)];')),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            expected_output = test_case[1]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.get_state_str()

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

# Tests for NW_Node's search_for_connection function
    def test_NW_Node_search_for_connection_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),]),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80),])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            param = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.search_for_connection(param)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node_search_for_connection_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(80), (type(None), None)),
            (('PC',[0,0,0,0],1.0,0.0,[([0,0,0,0],1,1,'TCP',80),]),(80), (str, '([0,0,0,0],1,1,TCP,80)')),
            (('PC',[0,0,0,0],1.0,0.0,[([0,0,0,0],1,1,'TCP',80),]),(81), (type(None), None)),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(80),(type(None),None)),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),(80),(str,'([0,0,0,1],1,1,TCP,80)')),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),(81),(str,'([0,0,0,2],3,4,UDP,81)')),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.search_for_connection(params_1)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    def test_NW_Node_search_for_connection_errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), None, (TypeError)),
            (('PC',[0,0,0,0],1.0,0.0,[]), 'string instance', (TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0.0,(TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),-1,(ValueError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),-1,(ValueError)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.search_for_connection(params_1)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's is_open_port function

    def test_NW_Node_is_open_port_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('PC',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),]),(80),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80),])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            param = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.is_open_port(param)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node_is_open_port_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(80), (bool, True)),
            (('PC',[0,0,0,0],1.0,0.0,[([0,0,0,0],1,1,'TCP',80),]),(80), (bool, False)),
            (('PC',[0,0,0,0],1.0,0.0,[([0,0,0,0],1,1,'TCP',80),]),(81), (bool, True)),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(80),(bool, True)),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),(80),(bool, False)),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),(81),(bool, False)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.is_open_port(params_1)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    def test_NW_Node_is_open_port_errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]), None, (TypeError)),
            (('PC',[0,0,0,0],1.0,0.0,[]), 'string instance', (TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),0.0,(TypeError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),-1,(ValueError)),
            (('Mobile',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81),]),-1,(ValueError)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.is_open_port(params_1)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's add_connection function

    def test_NW_Node_add_connection_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'TCP',80),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80)])),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             ([0,0,0,2],3,4,'UDP',81),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81)])),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             ([0,0,0,2],3,4,'UDP',80),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80)])),

            (('PC',[0,0,0,0],0.0,0.0,None),
             ([0,0,0,1],1,1,'TCP',80),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80)])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            param_dest_ip, param_cost, param_bandwidth, param_connection_type, param_source_port = params
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            try:
                result = new_node_1.add_connection(param_dest_ip, param_cost, param_bandwidth, param_connection_type, param_source_port)
            except:
                temp = 0 #do nothing if exception occurs, state must still be tested post-error
            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node_add_connection_errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            #Checking for incorrect parameter types
            (('PC',[0,0,0,0],0.0,0.0,[]),
             (None,1,1,'TCP',80),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],None,1,'TCP',80),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,None,'TCP',80),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,None,80),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'TCP',None),
             (TypeError)),

            #Checking for incorrect parameter values
            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'TCP',-1),
             (ValueError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],-1,1,'TCP',80),
             (ValueError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,-1,'TCP',80),
             (ValueError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'ADP',80),
             (ValueError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'ADP',-1),
             (ValueError)),

            #Checking for making a connection with an already in-use port
            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,2],2,2,'TCP',80)]),
             ([0,0,0,1],1,1,'TCP',80),
             (ValueError)),

        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            param_destination, param_cost, param_bandwidth, param_connection_type, param_source_port = params_1
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.add_connection(param_destination, param_cost, param_bandwidth, param_connection_type, param_source_port)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's remove_connection function

    def test_NW_Node_remove_connection_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             (80),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81)]),
             (81),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80)])),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             (81),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[([0,0,0,1],1,1,'TCP',80)])),

            (('PC',[0,0,0,0],0.0,0.0,None),
             (80),
             (NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            param_source_port = params
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            try:
                result = new_node_1.remove_connection(param_source_port)
            except:
                temp = 0 #do nothing if exception occurs, state must still be tested post-error
            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_node_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node_1.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node_1.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node_1.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node_1.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node_1.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node_1.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node_1.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node_1.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node_1.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node_1.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node_1.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node_1.connections,expected_connections))  # add assertion here

    def test_NW_Node_remove_connection_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             (80),
             (tuple,([0,0,0,1],1,1,'TCP',80))),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80),([0,0,0,2],3,4,'UDP',81)]),
             (81),
             (tuple,([0,0,0,2],3,4,'UDP',81))),

            (('PC',[0,0,0,0],0.0,0.0,[([0,0,0,1],1,1,'TCP',80)]),
             (81),
             (type(None),None)),

            (('PC',[0,0,0,0],0.0,0.0,None),
             (80),
             (type(None),None)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)

            #perform functions to be tested
            result = new_node_1.remove_connection(params_1)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    def test_NW_Node_remove_connection_errors(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            #Checking for incorrect parameter types
            (('PC',[0,0,0,0],0.0,0.0,[]),
             (None),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ('80'),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             (80.5),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             (80.0),
             (TypeError)),

            (('PC',[0,0,0,0],0.0,0.0,[]),
             ([0,0,0,1],1,1,'TCP',None),
             (TypeError)),

            #Checking for incorrect parameter values
            (('PC',[0,0,0,0],0.0,0.0,[]),
             (-1),
             (ValueError)),

        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            params_1 = test_case[1]
            expected_output = test_case[2]
            device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1 = inputs_1
            param_source_port = params_1
            expected_error = expected_output
            new_node_1 = NW_Node(device_type_1, ip_1, base_sec_level_1, risk_level_1, connections_1)


            with self.assertRaises(expected_error) as cm:
                # perform functions to be tested
                result = new_node_1.remove_connection(param_source_port)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception),
                             'Failed error test | expected: {}, got: {}'.format(expected_error, actual_exception))

# Tests for NW_Node's get_ip_str function

    def test_NW_Node_get_ip_str_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(NW_Node,'PC',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(NW_Node,'Mobile',[0,0,0,0],0.0,0.0,0.0,[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_connections = expected_output
            new_node = NW_Node(device_type, ip, base_sec_level, risk_level, connections)

            #run function to be tested
            result = new_node.get_ip_str()

            #assert state is now as expected
            self.assertEqual(expected_object_type, type(new_node), 'Failed type checking of object | got: {}, expected: {}'.format(type(new_node),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_connections, new_node.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node.connections,expected_connections))  # add assertion here

    def test_NW_Node_get_ip_str_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,[]),(str,'0.0.0.0')),
            (('Mobile',[0,0,0,0],0.0,0.0,[]),(str,'0.0.0.0')),
            (('Mobile',[0,0,0,0],0.0,0.0,None),(str,'0.0.0.0')),
            (('Mobile',[1,0,0,0],0.0,0.0,None),(str,'1.0.0.0')),
            (('Mobile',[0,1,0,0],0.0,0.0,None),(str,'0.1.0.0')),
            (('Mobile',[0,0,1,0],0.0,0.0,None),(str,'0.0.1.0')),
            (('Mobile',[0,0,0,1],0.0,0.0,[]),(str,'0.0.0.1')),
            (('Mobile',[255,0,0,0],0.0,0.0,None),(str,'255.0.0.0')),
            (('Mobile',[0,255,0,0],0.0,0.0,None),(str,'0.255.0.0')),
            (('Mobile',[0,0,255,0],0.0,0.0,[]),(str,'0.0.255.0')),
            (('Mobile',[0,0,0,255],0.0,0.0,None),(str,'0.0.0.255')),
            (('Mobile',[255,255,255,255],0.0,0.0,None),(str,'255.255.255.255')),
        ]
        for test_case in test_cases:
            #test setup
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, connections = inputs
            expected_return_type, expected_return_value = expected_output
            new_node = NW_Node(device_type, ip, base_sec_level, risk_level, connections)

            #run function to be tested
            result = str(new_node)

            #assert state is now as expected
            self.assertEqual(expected_return_type, type(result), 'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_type, type(result), 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

# Tests for NW_Sec_Device's __init__ funciton
    def test_NW_Sec_Device__init__state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,0.0,[],[]),
             (NW_Sec_Device,'PC',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),

            (('PC',[0,0,0,0],0.0,0.0,0.0,None,[]),
             (NW_Sec_Device,'PC',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),

            (('Mobile',[0,0,0,0],0.0,0.0,0.0,[],[]),
             (NW_Sec_Device,'Mobile',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),

            (('Mobile',[0,0,0,0],0.0,0.0,0.0,[],None),
             (NW_Sec_Device,'Mobile',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, sec_modifier, coverage, connections = inputs
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_modifier, expected_coverage, expected_connections = expected_output
            new_node = NW_Sec_Device(device_type, ip, base_sec_level, risk_level, sec_modifier, coverage, connections)
            self.assertEqual(expected_object_type, type(new_node), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_node),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_modifier, new_node.sec_modifier, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.sec_modifier,expected_modifier))  # add assertion here
            self.assertEqual(expected_coverage, new_node.covered_devices, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.covered_devices,expected_coverage))  # add assertion here
            self.assertEqual(expected_connections, new_node.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node.connections,expected_connections))  # add assertion here

    def test_NW_Sec_Device__init__error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('Typewriter',[0,0,0,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[256,0,0,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,256,0,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,0,256,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,0,0,256],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[-1,0,0,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,-1,0,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,0,-1,0],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,0,0,-1],0.0,0.0,0.0,[],[]),(ValueError)),
            (('PC',[0,0,0,0],0.0,0.0,0.0,[],()),(TypeError)),
            (('PC',[0,0,0,0],0.0,0.0,0.0,(),[]),(TypeError)),
            (('PC',[0,0,0,0],0.0,0.0,0.0,[],'Not a List'),(TypeError)),
            (('PC',[0,0,0,0],0.0,0.0,0.0,'Not a List',[]),(TypeError)),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, modifier, coverage, connections = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                NW_Sec_Device(device_type, ip, base_sec_level, risk_level, modifier, coverage, connections)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))

    def test_NW_Sec_Device__init__NONE_value_errors(self):
        """
        Test function to ensure that __init__ function for NW_Node handles incorrect input types
        :return:
        """
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((None,[0,0,0,0],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',None,0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',[None,0,0,0],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',[0,None,0,0],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',[0,0,None,0],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',[0,0,0,None],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',[0,0,0,0],None,0.0,0.0,[],[]),(TypeError)),
            (('PC',[0,0,0,0],0.0,None,0.0,[],[]),(TypeError)),
            (('PC',[0,0,0,0],0.0,0.0,None,[],[]),(TypeError)),
            (('PC',[0.1,0,0,0],0.0,0.0,0.0,[],[]),(TypeError)),
            ((1,[0,0,0,0],0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC',1,0.0,0.0,0.0,[],[]),(TypeError)),
            (('PC','0.0.0.0',0.0,0.0,0.0,[],[]),(TypeError)),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, modifier, coverage, connections = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                NW_Sec_Device(device_type, ip, base_sec_level, risk_level, modifier, coverage, connections)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))


# Tests for NW_Sec_Device's __str__ function
    def test_NW_Sec_Device__str__state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('PC',[0,0,0,0],0.0,0.0,0.0,[],[]),(NW_Sec_Device,'PC',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),
            (('Mobile',[0,0,0,0],0.0,0.0,0.0,[],[]),(NW_Sec_Device,'Mobile',[0,0,0,0],0.0,0.0,0.0,0.0,[],[])),
        ]
        for test_case in test_cases:
            #test setup
            inputs = test_case[0]
            expected_output = test_case[1]
            device_type, ip, base_sec_level, risk_level, modifier, coverage, connections = inputs
            expected_object_type, expected_device_type, expected_ip, expected_base_sec_level, expected_security_level, expected_risk_level, expected_modifier, expected_coverage, expected_connections = expected_output
            new_node = NW_Sec_Device(device_type, ip, base_sec_level, risk_level, modifier, coverage, connections)

            #run function to be tested
            result = str(new_node)

            #assert state is now as expected
            self.assertEqual(expected_object_type, type(new_node), 'Failed type checking of object | got: {}, expected: {}'.format(type(new_node),expected_object_type)) # add assertion here
            self.assertEqual(expected_device_type, new_node.device_type, 'Failed value checking of device_type | got: {}, expected: {}'.format(new_node.device_type,expected_device_type))  # add assertion here
            self.assertEqual(expected_ip, new_node.device_ip, 'Failed value checking of ip address | got: {}, expected: {}'.format(new_node.device_ip,expected_ip))  # add assertion here
            self.assertEqual(expected_base_sec_level, new_node.base_sec_level, 'Failed value checking of base_security_level | got: {}, expected: {}'.format(new_node.base_sec_level,expected_base_sec_level))  # add assertion here
            self.assertEqual(expected_security_level, new_node.security_level, 'Failed value checking of security_level | got: {}, expected: {}'.format(new_node.security_level,expected_security_level))  # add assertion here
            self.assertEqual(expected_risk_level, new_node.risk_level, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.risk_level,expected_risk_level))  # add assertion here
            self.assertEqual(expected_modifier, new_node.sec_modifier, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.sec_modifier,expected_modifier))  # add assertion here
            self.assertEqual(expected_coverage, new_node.covered_devices, 'Failed value checking of risk_level | got: {}, expected: {}'.format(new_node.covered_devices,expected_coverage))  # add assertion here
            self.assertEqual(expected_connections, new_node.connections, 'Failed value checking of connections | got: {}, expected: {}'.format(new_node.connections,expected_connections))  # add assertion here

if __name__ == '__main__':
    unittest.main()
