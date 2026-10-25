import unittest
from pathlib import Path
from src.data.IO.IOStream import IOStream, LogStream

system = "Mac"
def fix_paths(fpath):
    path = str(fpath)
    if system == "Win":
        fpath = str(fpath).replace("/","\\")
        return fpath
    if system == "Mac":
        fpath = str(fpath).replace("\\","/")
        return fpath

class IOStream_Test(unittest.TestCase):
    # Control tests; these should NEVER fail
    def test_pass(self):
        self.assertEqual(True, True)  # add assertion here

    def test_fail(self):
        self.assertNotEqual(True, False)  # add assertion here

    def test_IOStream__init__state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-1'),'r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-1'),True,False,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-2'),'w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-2'),False,True,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-3'),'rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-init-state-test-3'),True,True,True)),
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
            ((fix_paths('./test-files/iostream-init-error-test-1'),''),(ValueError)),
            ((fix_paths('./test-files/iostream-init-error-test-2'),'apple'),(ValueError)),
            ((fix_paths('./test-files/iostream-init-error-test-3'),'read'),(ValueError)),
            ((fix_paths('./test-files/iostream-init-error-test-4'),'write'),(ValueError)),

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
            ((fix_paths('src/data/IO/Testers/test-files/iostream-init-NONE-value-errors-test-1'),None),(TypeError)),

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
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-1'),'w'),('w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-1'),False,True,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-2'),'r'),('r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-2'),True,False,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-3'),'rw'),('rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-state-test-3'),True,True,True)),

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
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-error-test-1'),'w'),(''),(ValueError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-error-test-2'),'w'),('apple'),(ValueError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-error-test-3'),'w'),('x'),(ValueError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-error-test-4'),'w'),('b'),(ValueError)),

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
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-1'), 'w'), ('w'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-2'), 'w'), ('r'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-3'), 'r'), ('r'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-4'), 'r'), ('w'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-5'), 'rw'), ('rw'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-6'), 'rw'), ('r'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-7'), 'rw'), ('w'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-8'), 'w'), ('rw'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-check-permission-value-test-9'), 'r'), ('rw'), (bool, False)),
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

    # Testing for IOStream's close_file method
    def test_IOStream_close_file_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-1'),'w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-1'),False,True,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-2'),'r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-2'),True,False,True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-3'),'rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-close-file-state-test-3'),True,True,True)),

        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            fpath, mode = inputs_1
            # mode_arg = func_args
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_closed = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = new_stream_1.close_file()

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_closed, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_closed, test_no))  # add assertion here

    # Testing for IOStream's get_f_path method
    def test_IOStream_get_f_path_state(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-1'),'w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-1'),False,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-2'),'r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-2'),True,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-3'),'rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-state-test-3'),True,True,False)),

        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            fpath, mode = inputs_1
            # mode_arg = func_args
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = new_stream_1.get_f_path()

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_get_f_path_value(self):
        #a test case is a set of two tuples - inputs, expected results
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-1'), 'w'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-1'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-2'), 'r'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-2'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-3'), 'rw'), (str,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-3'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-4'), 'w'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-4'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-5'), 'r'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-5'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-6'), 'rw'), (str,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-6'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-7'), 'w'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-7'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-8'), 'r'), (str, fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-8'))),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-9'), 'rw'), (str,fix_paths('src/data/IO/Testers/test-files/iostream-get-f-path-value-test-9'))),
        ]
        for test_case in test_cases:
            #test setup
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            f_path, mode = inputs_1
            # mode_arg = func_args
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)

            #perform functions to be tested
            result = new_stream_1.get_f_path()

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {}'.format(type(result),expected_return_type)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {}'.format(result,expected_return_value)) # add assertion here

    # Testing for IOStream's get_can_read method
    def test_IOStream_get_can_read_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'get-can-read'
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1').format(fpath_func,test_type),'w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1').format(fpath_func,test_type),False,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2').format(fpath_func,test_type),'r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2').format(fpath_func,test_type),True,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3').format(fpath_func,test_type),'rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3').format(fpath_func,test_type),True,True,False)),

        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            fpath, mode = inputs_1
            # mode_arg = func_args
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = new_stream_1.get_can_read()

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_get_can_read_value(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'get-can-read'
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)), 'r'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)), 'w'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)), 'rw'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-4'.format(fpath_func,test_type)), 'r'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-5'.format(fpath_func,test_type)), 'w'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-6'.format(fpath_func,test_type)), 'rw'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-7'.format(fpath_func,test_type)), 'r'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-8'.format(fpath_func,test_type)), 'w'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-9'.format(fpath_func,test_type)), 'rw'), (bool, True)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            f_path, mode = inputs_1
            # mode_arg = func_args
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)

            #perform functions to be tested
            result = new_stream_1.get_can_read()

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}'.format(result,expected_return_value, test_no)) # add assertion here

    # Testing for IOStream's get_can_write method
    def test_IOStream_get_can_write_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'get-can-write'
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),'r'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),True,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),'w'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),False,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),'rw'),(IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),True,True,False)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            fpath, mode = inputs_1
            # mode_arg = func_args
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = new_stream_1.get_can_write()

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_get_can_write_value(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'get-can-write'
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)), 'r'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)), 'w'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)), 'rw'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-4'.format(fpath_func,test_type)), 'r'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-5'.format(fpath_func,test_type)), 'w'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-6'.format(fpath_func,test_type)), 'rw'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-7'.format(fpath_func,test_type)), 'r'), (bool, False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-8'.format(fpath_func,test_type)), 'w'), (bool, True)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-9'.format(fpath_func,test_type)), 'rw'), (bool, True)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            # func_args = test_case[1]
            expected_output = test_case[1]
            f_path, mode = inputs_1
            # mode_arg = func_args
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)

            #perform functions to be tested
            result = new_stream_1.get_can_write()

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}'.format(result,expected_return_value, test_no)) # add assertion here

    # Testing for IOStream's set_can_write method
    def test_IOStream_set_can_write_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'set-can-write'
        function_var = IOStream.set_can_write
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),'r'),
             (True,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),True,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),'w'),
             (False,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),False,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),'rw'),
             (True,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),True,True,False)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode = inputs_1
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_set_can_write_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'set-can-write'
        function_var = IOStream.set_can_write
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func, test_type)), 'r'),
             ('abc',),
             (TypeError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func, test_type)), 'w'),
             ('False',),
             (TypeError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func, test_type)), 'rw'),
             (1,),
             (TypeError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type = inputs
            expected_error = expected_output
            stream = IOStream(fpath, permission_type)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    # Testing for IOStream's set_can_read method
    def test_IOStream_set_can_read_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'set-can-read'
        function_var = IOStream.set_can_read
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),'r'),
             (False,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),False,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),'w'),
             (True,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),True,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),'rw'),
             (False,),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)),False,True,False)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode = inputs_1
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_set_can_read_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'set-can-read'
        function_var = IOStream.set_can_read
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func, test_type)), 'r'),
             ('abc',),
             (TypeError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func, test_type)), 'w'),
             ('False',),
             (TypeError)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func, test_type)), 'rw'),
             (1,),
             (TypeError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type = inputs
            expected_error = expected_output
            stream = IOStream(fpath, permission_type)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    # Testing for IOStream's read method
    def test_IOStream_read_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'read'
        function_var = IOStream.read
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),'r'),
             (),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),True,False,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),'rw'),
             (),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),True,True,False)),

        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode = inputs_1
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_read_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'read'
        function_var = IOStream.read
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func, test_type)), 'w'),
             (),
             (PermissionError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type = inputs
            expected_error = expected_output
            stream = IOStream(fpath, permission_type)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    def test_IOStream_read_value(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'read'
        function_var = IOStream.read
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)), 'r'),
             (),
             (list, ['This is a test'])),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)), 'rw'),
             (),
             (list, ['This is a multi-line test\n','This is the start of the next line'])),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)), 'r'),
             (),
             (list, ['This\n','is\n','a\n','very\n','multi\n','line\n','test'])),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            f_path, mode = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}'.format(result,expected_return_value, test_no)) # add assertion here


    # Test IOStream's write method
    def test_IOStream_write_state(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'write'
        function_var = IOStream.write
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),'w'),
             ('This is a single-line write test',),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)),False,True,False)),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),'rw'),
             ('This is a multi-line\nwrite test',),
             (IOStream,fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)),True,True,False)),

        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, mode = inputs_1
            expected_object_type, expected_fpath, expected_can_read, expected_can_write, expected_is_open = expected_output
            new_stream_1 = IOStream(fpath, mode)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_object_type, type(new_stream_1), 'Failed type checking of constructed object | got: {}, expected: {} for test{}'.format(type(new_stream_1),expected_object_type, test_no)) # add assertion here
            self.assertEqual(expected_fpath, new_stream_1.f_path, 'Failed value checking of fpath | got: {}, expected: {} for test{}'.format(new_stream_1.f_path,expected_fpath, test_no))  # add assertion here
            self.assertEqual(expected_can_read, new_stream_1.can_read, 'Failed value checking of can_read | got: {}, expected: {} for test{}'.format(new_stream_1.can_read,expected_can_read, test_no))  # add assertion here
            self.assertEqual(expected_can_write, new_stream_1.can_write, 'Failed value checking of can_write | got: {}, expected: {} for test{}'.format(new_stream_1.can_write,expected_can_write, test_no))  # add assertion here
            self.assertEqual(expected_is_open, new_stream_1.file.closed, 'Failed value checking of is_open | got: {}, expected: {} for test{}'.format(new_stream_1.file.closed,expected_is_open, test_no))  # add assertion here

    def test_IOStream_write_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'write'
        function_var = IOStream.write
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func, test_type)), 'r'),
             ('This is a single-line write test',),
             (PermissionError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type = inputs
            expected_error = expected_output
            stream = IOStream(fpath, permission_type)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    def test_IOStream_write_file_value(self):
        #a test case is a set of two tuples - inputs, expected results
        fpath_func = 'write'
        function_var = IOStream.write
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-1'.format(fpath_func,test_type)), 'w'),
             ('This is a test',),
             (list, ['This is a test'])),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-2'.format(fpath_func,test_type)), 'rw'),
             ('This is a multi-line test\nThis is the start of the next line',),
             (list, ['This is a multi-line test\n','This is the start of the next line'])),
            ((fix_paths('src/data/IO/Testers/test-files/iostream-{}-{}-test-3'.format(fpath_func,test_type)), 'w'),
             ('This\nis\na\nvery\nmulti\nline\ntest',),
             (list, ['This\n','is\n','a\n','very\n','multi\n','line\n','test'])),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            f_path, mode = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = IOStream(f_path, mode)


            #perform functions to be tested
            function_var(new_stream_1, *func_args)
            new_stream_1.__del__()
            new_stream_2 = IOStream(f_path, 'rw')
            result = new_stream_2.read()

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}'.format(result,expected_return_value, test_no)) # add assertion here

    # Test LogStream's __init__ method
    def test_LogStream__init__state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'init'
        function_var = class_type.get_id
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'w',1),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 1)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)), 'rw',2),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)),
              True, True, False, 2)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)), 'r',3),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)),
              True, False, False, 3)),

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
            self.assertEqual(expected_id, new_stream_1.log_id,
                             'Failed value checking of log_id | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.log_id, expected_id, test_no))  # add assertion here

    def test_LogStream__init__error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'init'
        function_var = class_type.get_id
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'w', '1'),
             (),
             (TypeError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type, id = inputs
            expected_error = expected_output
            with self.assertRaises(expected_error) as cm:
                stream = class_type(fpath, permission_type, id)
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    # Test LogStream's get_id method
    def test_LogStream_get_id_state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'get_id'
        function_var = class_type.get_id
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'w',1),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 1)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)), 'rw',2),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)),
              True, True, False, 2)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)), 'r',3),
             (),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)),
              True, False, False, 3)),

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
            self.assertEqual(expected_id, new_stream_1.log_id,
                             'Failed value checking of log_id | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.log_id, expected_id, test_no))  # add assertion here

    def test_LogStream_get_id_value(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'get_id'
        function_var = class_type.get_id
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func,test_type)), 'r', 1),
             (),
             (int, 1)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func,test_type)), 'w', 2),
             (),
             (int, 2)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func,test_type)), 'rw', 3),
             (),
             (int, 3)),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            f_path, mode, id = inputs_1
            expected_return_type, expected_return_value = expected_output
            new_stream_1 = class_type(f_path, mode, id)

            #perform functions to be tested
            result = function_var(new_stream_1, *func_args)

            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}'.format(result,expected_return_value, test_no)) # add assertion here

    # Test LogStream's log_command method
    def test_LogStream_log_command_state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-command'
        function_var = class_type.log_command
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'w',1),
             (('command 1','arg 1'),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 1)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)), 'w',2),
             (('command 2', 'arg 2'),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 2)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)), 'rw',3),
             (('COMMAND 3', 3),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)),
              True, True, False, 3)),

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
            self.assertEqual(expected_id, new_stream_1.log_id,
                             'Failed value checking of log_id | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.log_id, expected_id, test_no))  # add assertion here

    def test_LogStream_log_command_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-command'
        function_var = class_type.log_command
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'r', 1),
             (('command 1', 'arg 1'),),
             (PermissionError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type, id = inputs
            expected_error = expected_output
            stream = class_type(fpath, permission_type, id)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    def test_LogStream_log_command_file_value(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-command'
        function_var = class_type.log_command
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func,test_type)), 'w', 1),
             (('func 1', 'args 1'),),
             (str, 'Function Called: func 1'),
             (str, 'Params: args 1'),
             ),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func,test_type)), 'w', 2),
             (('func 2', 'args 2'),),
             (str, 'Function Called: func 2'),
             (str, 'Params: args 2'),
             ),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func,test_type)), 'w', 3),
             (('func 3', 'args 3'),),
             (str, 'Function Called: func 3'),
             (str, 'Params: args 3'),
             ),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output_1 = test_case[2]
            expected_output_2 = test_case[3]
            f_path, mode, id = inputs_1
            expected_return_type, expected_return_value = expected_output_1
            expected_return_type2, expected_return_value2 = expected_output_2
            new_stream_1 = class_type(f_path, mode, id)


            #perform functions to be tested
            function_var(new_stream_1, *func_args)
            new_stream_1.__del__()
            new_stream_2 = class_type(f_path, 'rw', 10)
            temp = new_stream_2.read()
            temp = temp[0].split('|')
            result = temp[1].strip()
            result2 = temp[2].strip()


            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}a'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}a'.format(result,expected_return_value, test_no)) # add assertion here
            self.assertEqual(expected_return_type2,type(result2),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}b'.format(type(result2),expected_return_type2, test_no)) # add assertion here
            self.assertEqual(expected_return_value2, result2, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}b'.format(result2,expected_return_value2, test_no)) # add assertion here

    # Test LogStream's log_error method
    def test_LogStream_log_error_state_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-error'
        function_var = class_type.log_error
        test_type = 'state'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'w',1),
             (('error 1','msg 1'),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 1)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)), 'w',2),
             (('error 2', 'msg 2'),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func, test_type)),
              False, True, False, 2)),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)), 'rw',3),
             (('ERROR 3', 3),),
             (LogStream, fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func, test_type)),
              True, True, False, 3)),

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
            self.assertEqual(expected_id, new_stream_1.log_id,
                             'Failed value checking of log_id | got: {}, expected: {} for test{}'.format(
                                 new_stream_1.log_id, expected_id, test_no))  # add assertion here

    def test_LogStream_log_error_error_tests(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-error'
        function_var = class_type.log_error
        test_type = 'error'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func, test_type)), 'r', 1),
             (('error 1', 'msg 1'),),
             (PermissionError)),
        ]
        for test_case in test_cases:
            test_no = test_cases.index(test_case) + 1
            inputs = test_case[0]
            func_args = test_case[1]
            expected_output = test_case[2]
            fpath, permission_type, id = inputs
            expected_error = expected_output
            stream = class_type(fpath, permission_type, id)
            with self.assertRaises(expected_error) as cm:
                function_var(stream, *func_args)
            actual_exception = cm.exception
            self.assertEqual(expected_error, type(actual_exception), 'Failed error test | expected: {}, got: {} for test no {}'.format(expected_error,actual_exception, test_no))

    def test_LogStream_log_error_file_value(self):
        #a test case is a set of two tuples - inputs, expected results
        class_type = LogStream
        class_type_str = 'logstream'
        fpath_func = 'log-error'
        function_var = class_type.log_error
        test_type = 'value'
        test_cases = [
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-1'.format(class_type_str,fpath_func,test_type)), 'w', 1),
             (('error 1', 'msg 1'),),
             (str, 'Error: error 1'),
             (str, 'Msg: msg 1'),
             ),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-2'.format(class_type_str,fpath_func,test_type)), 'w', 2),
             (('error 2', 'msg 2'),),
             (str, 'Error: error 2'),
             (str, 'Msg: msg 2'),
             ),
            ((fix_paths('src/data/IO/Testers/test-files/{}-{}-{}-test-3'.format(class_type_str,fpath_func,test_type)), 'w', 3),
             (('error 3', 'msg 3'),),
             (str, 'Error: error 3'),
             (str, 'Msg: msg 3'),
             ),
        ]
        for test_case in test_cases:
            #test setup
            test_no = test_cases.index(test_case) + 1
            inputs_1 = test_case[0]
            func_args = test_case[1]
            expected_output_1 = test_case[2]
            expected_output_2 = test_case[3]
            f_path, mode, id = inputs_1
            expected_return_type, expected_return_value = expected_output_1
            expected_return_type2, expected_return_value2 = expected_output_2
            new_stream_1 = class_type(f_path, mode, id)


            #perform functions to be tested
            function_var(new_stream_1, *func_args)
            new_stream_1.__del__()
            new_stream_2 = class_type(f_path, 'rw', 10)
            temp = new_stream_2.read()
            temp = temp[0].split('|')
            result = temp[1].strip()
            result2 = temp[2].strip()


            #assert that actual is expected
            self.assertEqual(expected_return_type,type(result),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}a'.format(type(result),expected_return_type, test_no)) # add assertion here
            self.assertEqual(expected_return_value, result, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}a'.format(result,expected_return_value, test_no)) # add assertion here
            self.assertEqual(expected_return_type2,type(result2),  'Failed type checking of returned value | got: {}, expected: {} for test no. {}b'.format(type(result2),expected_return_type2, test_no)) # add assertion here
            self.assertEqual(expected_return_value2, result2, 'Failed value checking of returned value | got: {}, expected: {} for test no. {}b'.format(result2,expected_return_value2, test_no)) # add assertion here


if __name__ == '__main__':
    unittest.main()
