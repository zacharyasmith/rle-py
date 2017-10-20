import serial
import time
import signal


def _timeout(signum, frame):
    raise Exception("Timeout.")


class Serial:
    """This setup class is specified to work with the current (Oct 2017)
    boot loader on the LD2100, LD5200."""
    
    __conn = None
    __device_file = ''
    __conn_tries = 1
    __max_tries = 3
    
    def __init__(self, device_file):
        """Construct setup with 9600 baud > device file"""
        # Initialize timeout
        signal.signal(signal.SIGALRM, _timeout)
        # Initialize serial conn
        self.__device_file = device_file
        self.__conn = serial.Serial(self.__device_file)
        self._verify_connection()

    def open(self):
        if not self.__conn.is_open:
            self.__conn.open()
            self._verify_connection()

    def _verify_connection(self):
        """Verifies connection."""
        # Reading variable
        print('Verifying connection with ' + self.__device_file)
        line = ''
        # Start timeout
        signal.alarm(5)
        # init help function
        self.__conn.write(b'?\n')
        try:
            while line != b'run    - run the flash application\r\n':
                line = self.__conn.readline()
        except Exception:
            self.__conn_tries += 1
            if self.__conn_tries < self.__max_tries:
                print("Retrying... Attempt {} of {}".format(self.__conn_tries, self.__max_tries))
                # recurse
                self._verify_connection()
            else:
                self.__conn_tries = 1
                print("Connection failed after {} attempts".format(self.__max_tries))
        print('Connection succeeded.')
        
    def close(self):
        """Close connection."""
        print('Closing connection with ' + self.__device_file)
        self.__conn.close()


if __name__ == "__main__":
    time.sleep(10)
    serial = Serial('/dev/ttyUSB0')

