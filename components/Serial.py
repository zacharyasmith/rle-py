"""
components/Serial.py

Author:
    Zachary Smith
"""
import re
import logging
from time import sleep
from datetime import datetime, timedelta

import serial
from components.Exceptions import TimeoutException, ConnectionRefusalException

_LOGGER = logging.getLogger()


class Serial(object):
    """
    This setup class is specified to work with the current
    boot loader on the LD2100, LD5200.
    """

    __conn_tries = 1
    __max_tries = 3

    def __init__(self, device_file):
        """
        Construct serial setup with 9600/N/8/1 >> device file

        Args:
            device_file: e.g. /dev/ttyUSB0
        """
        # Initialize serial conn
        self.__device_file = device_file
        self.__conn = serial.Serial(self.__device_file, timeout=10)
        self._verify_connection()
        self.__timeout_start = None # type: datetime
    
    def _check_timeout(self, timeout, timeout_start):
        difference = datetime.now() - timeout_start  # type: timedelta
        if difference.total_seconds() >= timeout:
            raise TimeoutException()

    def reset_input_buffer(self):
        """
        Resets the buffer to empty.
        """
        _LOGGER.debug('Serial::reset_input_buffer:: Flushing input buffer.')
        self.__conn.flushInput()
        sleep(.1)

    def read_line(self, timeout=0.5):
        """
        Read line and return char array
        Read line and return char array

        Returns:
            Byte string of chars
        """
        # Initialize timeout
        timeout_start = datetime.now()
        ret_val = b''
        try:
            while ret_val[-1:] != b'\n' or ret_val[-1:] is None:
                self._check_timeout(timeout, timeout_start)
                if self.__conn.inWaiting() > 0:
                    ret_val += self.__conn.read()
        except TimeoutException:
            _LOGGER.debug("Serial::read_line:: Timeout raised.")
        _LOGGER.debug('Serial::read_line:: Read line: {}'.format(str(ret_val)))
        return ret_val

    def send_command(self, command):
        """
        Sends command to the board.

        Args:
            command: byte array to send over serial comm link
        """
        self.__conn.write(command)
        _LOGGER.debug('Serial::send_command:: Wrote: {}'.format(str(command)))
        self.__conn.reset_output_buffer()
        sleep(.5)

    def read_stop(self, command, regex=r'', timeout=5):
        """
        Sends command to board. Returns content until stop string satisfied or timeout (s).
        Raises ConnectionRefusalException. Returns byte array of ASCII chars response.

        Args:
            command: Byte array to send over serial comm link
            regex: String to test response for to stop and return
            timeout: Time to wait until regex string is matched before exception raised

        Returns:
            Full byte array response up to and including matching regex line
        """
        _LOGGER.debug('Serial::read_stop:: Sending: {}'.format(command))
        _LOGGER.debug('Serial::read_stop:: Expecting regex: {}'.format(regex))
        # compile regex
        _re = re.compile(regex)
        # send the command
        self.send_command(command)
        # return variable
        ret_val = b''
        # Initialize timeout
        timeout_start = datetime.now()
        found = False
        try:
            while not found:
                self._check_timeout(timeout, timeout_start)
                # grab response
                line = self.read_line()
                ret_val += line
                # set found lv
                found = _re.search(str(line))
        except TimeoutException:
            _LOGGER.debug("Serial::read_stop:: Timeout raised.")
            if timeout != 5:
                raise TimeoutException
        finally:
            self.reset_input_buffer()
        return ret_val

    def open(self):
        """
        Opens connection with board if closed.
        """
        _LOGGER.info('Serial::open:: Opening connection...')
        if not self.__conn.is_open:
            self.__conn.open()
            self._verify_connection()
        else:
            _LOGGER.info('Serial::open:: Connection already open.')

    def _verify_connection(self, timeout=7):
        """
        Verifies connection.

        Args:
            timeout: Time allowed before retry or exception raise
        """
        if self.__conn_tries > self.__max_tries:
            # reset connection tries
            self.__conn_tries = 1
            raise ConnectionRefusalException('Connection failed after {} attempts'
                                             .format(self.__max_tries))
        # Reading variable
        _LOGGER.info('Serial::_verify_connection:: Verifying connection with {}'
                     .format(self.__device_file))
        line = ''
        # Initialize timeout
        timeout_start = datetime.now()
        # clear input
        self.__conn.reset_input_buffer()
        # init help function
        self.__conn.write(b'?\r\n')
        try:
            # last line of main menu in boot loader
            while line != b'run    - run the flash application\r\n':
                self._check_timeout(timeout, timeout_start)
                line = self.read_line()
            # reset connection tries
            self.__conn_tries = 1
            _LOGGER.info('Serial::_verify_connection:: Connection succeeded.')
        except TimeoutException:
            self.__conn_tries += 1
            if self.__conn_tries <= self.__max_tries:
                _LOGGER.info('Serial::_verify_connection:: Retrying... Attempt {} of {}'
                             .format(self.__conn_tries, self.__max_tries))
            # recurse
            self._verify_connection(timeout)

    def close(self):
        """
        Close connection.
        """
        _LOGGER.info('Serial::close:: Closing connection with {}'.format(self.__device_file))
        self.__conn.close()
