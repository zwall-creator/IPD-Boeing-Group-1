import os
import time

class IOStream:

    def __init__(self, f_path = '', read_write_type = 'r'):
        """
        :type: f_path: string
        :type: read_write_type: string

        :param f_path: path to file
        :param read_write_type: string indicating read/write permissions
        """
        self.f_path = f_path
        if read_write_type == 'r':
            self.can_read = True
            self.can_write = False
        if read_write_type == 'w':
            self.can_write = True
            self.can_read = False
        if read_write_type == 'rw':
            self.can_read = True
            self.can_write = True
        # Opening file during IOStream construction
        permission_type = ''
        if self.can_read:
            permission_type += 'r'
        if self.can_write:
            permission_type += 'w'
        # TODO: Send IOStream Update that file was opened
        self.file = open(self.f_path, permission_type)

    def check_permission(self, access_type):
        if access_type == 'r' or access_type == 'rw' or access_type == 'read':
            return self.can_read
        if access_type == 'w' or access_type == 'rw' or access_type == 'write':
            return self.can_write
        raise ValueError('arg access_type must be \'r\' or \'rw\' or \'w\'')

    def close_file(self):
        """
        Function to close the file, if still open
        """
        if self.file is not None:
            #TODO: Send IOStream Update that file was closed
            self.file.close()

    def __del__(self):
        """
        Function to close the file if this IOStream object is deconstructed
        """
        self.close_file()

    def get_f_path(self):
        """
        :return: path to file
        """
        return self.f_path

    def get_can_read(self):
        """
        :return: can_read
        """
        return self.can_read

    def get_can_write(self):
        """
        :return: can_write
        """
        return self.can_write

    def set_can_read(self, can_read):
        """
        :type can_read: bool
        :param can_read: new reading permissions
        """
        self.can_read = can_read

    def set_can_write(self, can_write):
        """
        :type can_write: bool
        :param can_write: new writing permissions
        """
        self.can_write = can_write


    #IOStream's read and write methods
    def read(self):
        """
        Function to read all data from a file, given that the stream has the correct permissions
        :return: string of the file contents
        """
        if not self.can_read:
            raise PermissionError('Permission to read file is invalid')
        return self.file.readlines()

    def readline(self):
        """
        Function to read a line from a file, given that the stream has the correct permissions
        :return: string of the contents of the file's read line
        """
        if not self.can_read:
            raise PermissionError('Permission to read file is invalid')
        return self.file.readline()

    def readlines(self, num_lines = -1):
        """
        Function to read a number of lines from a file, given that the stream has the correct permissions
        :type num_lines: int
        :param num_lines: number of lines to read
        :return: list of strings containing the contents of the file's read lines
        """
        if not self.can_read:
            raise PermissionError('Permission to read file is invalid')
        lines = self.file.readlines()
        if num_lines == -1:
            num_lines = len(lines)
        retlist = []
        for i in range(num_lines):
            retlist.append(lines[i].strip())
        return retlist

    def write(self, data):
        """
        Function to write data to a file, given that the stream has the correct permissions
        :type data: string containing the data to write
        :param data: data to write to file
        \n NOTE: the data to write must include user-written newline characters.
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        self.file.write(data)

    def get_timestamp(self):
        timestamp = time.localtime()
        return '{Month}/{Day}/{Year} {Hours}:{Minutes}:{Seconds}'.format(
            Month = timestamp.tm_mon,
            Day = timestamp.tm_mday,
            Year = timestamp.tm_year,
            Hours = timestamp.tm_hour,
            Minutes = timestamp.tm_min,
            Seconds = timestamp.tm_sec
        )

class LogStream(IOStream):
    def __init__(self, f_path = '', read_write_type = 'r', log_id = -1):
        """
        :param f_path:
        :param read_write_type:
        """
        super(LogStream, self).__init__(f_path, read_write_type)
        self.log_id = log_id

    def __del__(self):
        super().__del__()

    def get_id(self):
        """
        :return: log_id
        """
        return self.log_id

    def read_log(self):
        """
        :return: list of log contents
        """
        return self.read()

    def log_command(self, command):
        """
        Function to write a command entry to the log file
        :param command: Set containing the function and a list of that function's arguments
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        cmd, args = command
        #TODO: Update timestamp to call get_timestamp() once the function is implemented
        func_record = '{timestamp} | Function Called: {func} | Params: {params}\n'.format(timestamp=self.get_timestamp(),func=cmd,params=args)
        self.file.write(func_record)

    def log_error(self, error):
        """
        Function to write an error entry to the log file
        :param error: Set containing the error type and a string of its error message
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        err, msg = error
        #TODO: Update timestamp to call get_timestamp() once the function is implemented
        error_record = '{timestamp} | Error: {error_type} | Msg: {error_msg}'.format(timestamp=self.get_timestamp(),error_type=err,error_msg=msg)
        self.file.write(error_record)

    def log_warning(self, warning):
        """
        Function to write a warning entry to the log file
        :param warning: Set containing the warning type and a string of its warning message
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        wng, msg = warning
        #TODO: Update timestamp to call get_timestamp() once the function is implemented
        warning_record = '{timestamp} | Warning: {warning_type} | {warning_msg}'.format(timestamp=self.get_timestamp(),warning_type=wng,warning_msg=msg)
        self.file.write(warning_record)

    def log_event(self, event):
        """
        Function to write a user input event entry to the log file
        :param event: Set containing the event type and a string of its event details
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        evt, msg = event
        #TODO: Update timestamp to call get_timestamp() once the function is implemented
        input_record = '{timestamp} | Event: {event} | Details: {details}\n'.format(timestamp=self.get_timestamp(),event=evt,details=msg)
        self.file.write(input_record)

    def log_info(self, info):
        """
        Function to write a misc info entry to the log file
        :param info: string containing misc info to record
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')
        #TODO: Update timestamp to call get_timestamp() once the function is implemented
        info_record = '{timestamp} | Info: {info}'.format(timestamp=self.get_timestamp(),info=info)
        self.file.write(info_record)


class ReportStream(IOStream):
    def __init__(self, f_path = '', read_write_type = 'r', report_id = -1):
        super(ReportStream, self).__init__(f_path, read_write_type)
        self.report_id = report_id

    def __del__(self):
        super().__del__()

    def get_id(self):
        return self.report_id

    def write_report(self, log_id, state_str, runtime, completed_run, chosen_algorithm, solution_state_str):
        """
        Function to write a report entry to the report file, if correct permissions are present
        :type log_id: int
        :type state_str: str
        :type runtime: int
        :type completed_run: bool
        :type chosen_algorithm: str
        :type solution_state_str: str

        :param log_id: ID number of the associated log file
        :param state_str: A valid problem state string for the associated simulation network
        :param runtime: The number of seconds it took for the simulation to finish
        :param completed_run: Boolean indicator of if the simulation was completed or not
        :param chosen_algorithm: The algorithm that was the most effective
        :param solution_state_str: The state string for the simulation solution

        :raises PermissionError: if have insufficient permissions to write to this stream's file
        """
        if not self.can_write:
            raise PermissionError('Permission to write data is invalid')

        report_entry = ('Report No. {reportID}\n'
                        'Log No. {logID}\n'
                        'State Str: {stateStr}\n'
                        'Runtime: {runtime}\n'
                        'Completed Run: {completedRun}\n'
                        'Algorithm Chosen: {chosenAlgorithm}\n'
                        'Solution State Str: {solutionStateStr}\n').format(
            reportID=self.get_id(),
            logID=log_id,
            stateStr=state_str,
            runtime=runtime,
            completedRun=completed_run,
            chosenAlgorithm=chosen_algorithm,
            solutionStateStr=solution_state_str
        )

        self.file.write(report_entry)






