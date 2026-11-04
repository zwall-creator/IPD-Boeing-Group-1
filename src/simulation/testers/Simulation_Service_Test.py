import unittest
from src.simulation.Simulation_Service import Simulation_Service
from src.simulation.NW_Structure import *


class Simulation_Service_Test(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_Simulation_Service__init__state_tests(self):
        # a test case is a set of two tuples - inputs, expected results
        class_type = Simulation_Service
        class_type_str = 'simulation-service'
        fpath_func = 'init'
        function_var = class_type.__str__
        test_type = 'state'
        test_cases = [
            ( #Test Case 1
                (00000000, '', None), #constructor vals
                (), #funciton args
                (00000000, '', None)
            ),
        ]
        for test_case in test_cases:
            # test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode, id = inputs_1
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open, expected_id = expected_output
            new_stream_1 = class_type(fpath, mode, id)

            # perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            # assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1),
                             'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(
                                 type(new_stream_1), expected_object_type, test_no))  # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path,
                             'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.f_path, expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read,
                             'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.can_read, expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write,
                             'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.can_write, expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed,
                             'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.file.closed, expected_is_open, test_no))  # add assertion here
            self.assertEqual(expected_id, new_stream_1.solution_id,
                             'Failed value checking of log_id | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.solution_id, expected_id, test_no))  # add assertion here


if __name__ == '__main__':
    unittest.main()
