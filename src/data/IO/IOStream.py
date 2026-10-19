import os

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
        Function to read data from a file, given that the stream has the correct permissions
        :return: string of the file contents
        """
        #TODO: Implement IOStream's Read function
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
        :param data: data to write to file
        :return: True if success, False otherwise
        """
        #TODO: Implement IOStream's Write Function
        return NotImplemented

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
        return NotImplemented

    def log_command(self, command):
        return NotImplemented

    def log_error(self, error):
        return NotImplemented

    def log_warning(self, warning):
        return NotImplemented

    def log_event(self, event):
        return NotImplemented

    def log_info(self, info):
        return NotImplemented









