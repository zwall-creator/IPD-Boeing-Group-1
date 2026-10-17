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

    def get_f_path(self):
        """
        :return: path to file
        """
        return self.f_path

    def get_can_read(self):
        """
        :return: can_read
        :return:
        """
        return self.can_read

    def get_can_write(self):
        """
        :return: can_write
        :return:
        """
        return self.can_write

    def set_can_read(self, can_read):
        """
        :param can_read: new reading permissions
        """
        self.can_read = can_read

    def set_can_write(self, can_write):
        """
        :param can_write: new writing permissions

        """
        self.can_write = can_write

    def read(self):
        """
        Function to read data from a file, given that the stream has the correct permissions
        :return: string of the file contents
        """
        #TODO: Implement IOStream's Read function
        return NotImplemented

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

    def get_id(self):
        return self.log_id

    def read_log(self):
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









