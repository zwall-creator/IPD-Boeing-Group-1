import unittest

from src.simulation.NW_Structure import NW_Node, NW_Sec_Device


class NW_Structure_Test(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

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



if __name__ == '__main__':
    unittest.main()
