import serial
import time
import signal
import re


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ConnectionRefusalException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


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
        """Construct setup with 9600 baud > device file"""
        # Initialize serial conn
        self.__device_file = device_file
        self.__conn = serial.Serial(self.__device_file)
        self._verify_connection()

    def send_command(self, command):
        """Sends command to the board."""
        self.__conn.write(command)

    def read_stop(self, command, regex=r'\\r\\n', timeout=5):
        """Sends command to board. Returns content until stop string satisfied or timeout (s).
        Raises ConnectionRefusalException."""
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
        while not found:
            # grab response
            line = self.__conn.readline()
            ret_val += line
            # set found lv
            found = _re.search(str(line))
        return ret_val

    def open(self):
        """Opens connection with board if closed."""
        print('Serial:: Opening connection...')
        if not self.__conn.is_open:
            self.__conn.open()
            self._verify_connection()
        else:
            print('Serial:: Connection already open.')

    def _verify_connection(self):
        """Verifies connection."""
        # Reading variable
        print('Serial:: Verifying connection with ' + self.__device_file)
        line = ''
        # Initialize timeout
        signal.signal(signal.SIGALRM, _timeout)
        # Start timeout
        signal.alarm(5)
        # init help function
        self.__conn.write(b'?\n')
        try:
            # last line of main menu in boot loader
            while line != b'run    - run the flash application\r\n':
                line = self.__conn.readline()
        except TimeoutException:
            self.__conn_tries += 1
            if self.__conn_tries < self.__max_tries:
                print('Serial:: Retrying... Attempt {} of {}'.format(self.__conn_tries, self.__max_tries))
                # recurse
                self._verify_connection()
            else:
                self.__conn_tries = 1
                raise ConnectionRefusalException('Connection failed after {} attempts'.format(self.__max_tries))
        print('Serial:: Connection succeeded.')

    def close(self):
        """Close connection."""
        print('Serial:: Closing connection with ' + self.__device_file)
        self.__conn.close()


if __name__ == "__main__":
    time.sleep(10)
    serial = Serial('/dev/ttyUSB0')
