from components.Exceptions import TimeoutException, ConnectionRefusalException
import serial
import time
import signal
import re


def _timeout(signum, frame):
    raise TimeoutException('Timeout.')


class Serial:
    """This setup class is specified to work with the current (Oct 2017)
    boot loader on the LD2100, LD5200."""

    __conn = None
    __device_file = ''
    __conn_tries = 1
    __max_tries = 3

    def __init__(self, device_file):
        """
        Construct serial setup with 9600/N/8/1 >> device file

        :param device_file: e.g. /dev/ttyUSB0
        """
        # Initialize serial conn
        self.__device_file = device_file
        self.__conn = serial.Serial(self.__device_file)
        self._verify_connection()

    def read_line(self):
        """
        Read line and return char array
        :return: Byte string of chars
        """
        ret_val = b''
        while ret_val[-1:] != b'\n' or ret_val[-1:] is None:
            ret_val += self.__conn.read()
        return ret_val

    def send_command(self, command):
        """
        Sends command to the board.

        :param command: byte array to send over serial comm link
        """
        self.__conn.write(command)
        self.__conn.reset_output_buffer()

    def read_stop(self, command, regex=r'', timeout=5):
        """
        Sends command to board. Returns content until stop string satisfied or timeout (s).
        Raises ConnectionRefusalException. Returns byte array of ASCII chars response.

        :param command: Byte array to send over serial comm link
        :param regex: String to test response for to stop and return
        :param timeout: Time to wait until regex string is matched before exception raised
        :return: Full byte array response up to and including matching regex line
        """
        # compile regex
        _re = re.compile(regex)
        # send the command
        self.send_command(command)
        # return variable
        ret_val = b''
        # Initialize timeout
        signal.signal(signal.SIGALRM, _timeout)
        # start timeout
        signal.alarm(timeout)
        found = False
        try:
            while not found:
                # grab response
                line = self.__conn.readline()
                ret_val += line
                # set found lv
                found = _re.search(str(line))
        finally:
            self.__conn.reset_input_buffer()
        return ret_val

    def open(self):
        """
        Opens connection with board if closed.
        """
        print('Serial::open:: Opening connection...')
        if not self.__conn.is_open:
            self.__conn.open()
            self._verify_connection()
        else:
            print('Serial::open:: Connection already open.')

    def _verify_connection(self, timeout=7):
        """
        Verifies connection.

        :param timeout: Time allowed before retry or exception raise
        """
        if self.__conn_tries > self.__max_tries:
            # reset connection tries
            self.__conn_tries = 1
            raise ConnectionRefusalException('Connection failed after {} attempts'.format(self.__max_tries))
        # Reading variable
        print('Serial::_verify_connection:: Verifying connection with', self.__device_file)
        line = ''
        # Initialize timeout
        signal.signal(signal.SIGALRM, _timeout)
        # Start timeout
        signal.alarm(timeout)
        # init help function
        self.__conn.write(b'?\r\n')
        try:
            # last line of main menu in boot loader
            while line != b'run    - run the flash application\r\n':
                line = self.__conn.readline()
            # reset connection tries
            self.__conn_tries = 1
            signal.alarm(0)
            print('Serial::_verify_connection:: Connection succeeded.')
        except TimeoutException:
            self.__conn_tries += 1
            if self.__conn_tries <= self.__max_tries:
                print('Serial::_verify_connection:: Retrying... Attempt {} of {}'.format(self.__conn_tries, self.__max_tries))
            # recurse
            self._verify_connection(timeout)

    def close(self):
        """
        Close connection.
        """
        print('Serial::close:: Closing connection with', self.__device_file)
        self.__conn.close()


if __name__ == "__main__":
    time.sleep(10)
    serial = Serial('/dev/ttyUSB0')
