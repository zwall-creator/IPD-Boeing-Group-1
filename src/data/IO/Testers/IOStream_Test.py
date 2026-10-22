import unittest
from src.data.IO.IOStream import IOStream

class IOStream_Test(unittest.TestCase):
    # Control tests; these should NEVER fail
    def test_pass(self):
        self.assertEqual(True, True)  # add assertion here

    def test_fail(self):
        self.assertNotEqual(True, False)  # add assertion here

    def test_IOStream__init__state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('src/data/IO/Testers/test-files/iostream-init-state-test-1','r'),(IOStream,'src/data/IO/Testers/test-files/iostream-init-state-test-1',True,False,True)),
            (('src/data/IO/Testers/test-files/iostream-init-state-test-2','w'),(IOStream,'src/data/IO/Testers/test-files/iostream-init-state-test-2',False,True,True)),
            (('src/data/IO/Testers/test-files/iostream-init-state-test-3','rw'),(IOStream,'src/data/IO/Testers/test-files/iostream-init-state-test-3',True,True,True)),
        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            fpath, permission_type = inputs
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream = IOStream(fpath, permission_type)
            self.assertEqual(expected_object_type, type(new_stream), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_stream),expected_object_type)) # add assertion here
            self.assertEqual(expected_fpath, new_stream.f_path, 'Failed value checking of fpath | got: {}, expected: {}'.format(new_stream.f_path,expected_fpath))  # add assertion here
            self.assertEqual(expected_can_read, new_stream.can_read, 'Failed value checking of can_read | got: {}, expected: {}'.format(new_stream.can_read,expected_can_read))  # add assertion here
            self.assertEqual(expected_can_write, new_stream.can_write, 'Failed value checking of can_write | got: {}, expected: {}'.format(new_stream.can_write,expected_can_write))  # add assertion here
            self.assertEqual(expected_is_open, new_stream.file is not None, 'Failed value checking of file open state | got: {}, expected: {}'.format(new_stream.file is not None,expected_is_open))  # add assertion here
            # new_stream.close_file()

    def test_IOStream__init__error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('','r'),(FileNotFoundError)),
            (('./test-files/iostream-init-error-test-1',''),(ValueError)),
            (('./test-files/iostream-init-error-test-2','apple'),(ValueError)),
            (('./test-files/iostream-init-error-test-3','read'),(ValueError)),
            (('./test-files/iostream-init-error-test-4','write'),(ValueError)),

        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            fpath, permission_type = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                IOStream(fpath, permission_type)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))

    def test_IOStream__init__NONE_value_errors(self):
        """
        Test function to ensure that __init__ function for IOStream handles incorrect input types
        :return:
        """
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((None,'r'),(TypeError)),
            ((None,'w'),(TypeError)),
            ((None,'rw'),(TypeError)),
            (('src/data/IO/Testers/test-files/iostream-init-NONE-value-errors-test-1',None),(TypeError)),

        ]
        for test_case in test_cases:
            inputs = test_case[0]
            expected_output = test_case[1]
            fpath, mode = inputs
            expected_error = expected_output

            with self.assertRaises(expected_error) as cm:
                IOStream(fpath, mode)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))

    # testing for IOStream's check_permission function
    def test_IOStream_check_permission_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('src/data/IO/Testers/test-files/iostream-check-permission-state-test-1','w'),('w'),(IOStream,'src/data/IO/Testers/test-files/iostream-check-permission-state-test-1',False,True,True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-state-test-2','r'),('r'),(IOStream,'src/data/IO/Testers/test-files/iostream-check-permission-state-test-2',True,False,True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-state-test-3','rw'),('rw'),(IOStream,'src/data/IO/Testers/test-files/iostream-check-permission-state-test-3',True,True,True)),

        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode = inputs_1
            mode_arg = func_args
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = new_stream_1.check_permission(mode_arg)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {}'.format(type(new_stream_1),expected_object_type)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {}'.format(new_stream_1.f_path,expected_fpath))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {}'.format(new_stream_1.can_read,expected_can_read))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {}'.format(new_stream_1.can_write,expected_can_write))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file is not None, 'Failed value checking of is_open | got: {}, expected: {}'.format(new_stream_1.file is not None,expected_is_open))  # add assertion here

    def test_IOStream_check_permission_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('src/data/IO/Testers/test-files/iostream-check-permission-error-test-1','w'),(''),(ValueError)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-error-test-2','w'),('apple'),(ValueError)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-error-test-3','w'),('x'),(ValueError)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-error-test-4','w'),('b'),(ValueError)),

        ]
        for test_case in test_cases:
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type = inputs
            mode_arg = func_args
            expected_error = expected_output
            stream = IOStream(fpath, permission_type)
            with self.assertRaises(expected_error) as cm:
                stream.check_permission(mode_arg)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {}'.format(expected_error,actual_exception))

    def test_IOStream_check_permission_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-1', 'w'), ('w'), (bool, True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-2', 'w'), ('r'), (bool, False)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-3', 'r'), ('r'), (bool, True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-4', 'r'), ('w'), (bool, False)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-5', 'rw'), ('rw'), (bool, True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-6', 'rw'), ('r'), (bool, True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-7', 'rw'), ('w'), (bool, True)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-8', 'w'), ('rw'), (bool, False)),
            (('src/data/IO/Testers/test-files/iostream-check-permission-value-test-9', 'r'), ('rw'), (bool, False)),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            f_path, mode = inputs_1
            mode_arg = func_args
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)

            #perform functions to be tested
            result = new_stream_1.check_permission(mode_arg)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here


if __name__ == '__main__':
    unittest.main()
