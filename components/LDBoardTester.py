"""
components/LDBoardTester.py

Author:
    Zachary Smith
"""
import datetime
import logging
import re
import signal
import subprocess
import threading
from struct import pack
from time import sleep

from components.Exceptions import OperationsOutOfOrderException, TimeoutException
from components.ModBus import ModBus
from components.Serial import Serial

_LOGGER = logging.getLogger()

# used as shared variable between threads
_THREAD_READ_INDEX = -1


def timeout_handler():
    """
    Used in alarm contexts.
    """
    raise TimeoutException('Timeout.')


class ExecuteModBusThread(threading.Thread):
    """
    Initiates and runs separate thread for sending ModBus signals over RS485
    """
    def __init__(self, slave, start, num_ports):
        """
        Constructor
        Args:
            slave: binary slave index (usually 0)
            start: binary start register
            num_ports: binary number of ports
        """
        threading.Thread.__init__(self)
        _LOGGER.debug('ExecuteModBusThread:: Creating thread.')
        self.__serial_modbus = ModBus("serial", device_file='/dev/ttyUSB0', timeout=0)
        self.__slave = slave
        self.__start = start
        self.__num_ports = num_ports

    def __del__(self):
        """
        Destructor.
        """
        self.__serial_modbus.close()

    def run(self):
        """
        The runner command which sends commands over ModBus
        """
        global _THREAD_READ_INDEX
        # wait for listener
        while _THREAD_READ_INDEX < 0:
            pass
        while _THREAD_READ_INDEX < self.__num_ports:
            # write at 10hz
            sleep(0.1)
            # TODO switch Mux to thread_read_index
            # send command
            self.__serial_modbus.read_input_registers(self.__start, unit=self.__slave)


class LDBoardTester(object):
    """
    Class for testing the leak detection boards.
    """
    __serial = None
    __date_set = None

    def __init__(self):
        """
        Constructor
        """
        self.__serial = Serial('/dev/ttyUSB1')

    def __enter__(self):
        """
        Entry
        Returns:
            self
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit method
        Args:
            exc_type:
            exc_val:
            exc_tb:
        """
        self.__serial.close()

    def configure_ip_address(self, ip_address):
        """
        Configures IP address by writing command to bootloader

        Args:
            ip_address: The IP address to set

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::configure_ip_address:: Configuring board\'s IP address as {}'
                     .format(ip_address))
        self.__serial.send_command(b'ip ' + ip_address.encode('ascii') + b'\n')
        result = self.__serial.read_stop(b'netcfg\n', r'ip: {}'.format(ip_address))
        if not result:
            _LOGGER.error('LDBoardTest::configure_ip_address:: Configuration failed.')
            return False
        return True

    def test_ethernet(self, ip_address='10.0.0.188', configure_ip_address=False):
        """
        Test the Ethernet connection with a ping.

        Args:
            ip_address: IP address to ping, verifying Ethernet HW
            configure_ip_address: If True, will configure board's IP address to match

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::test_ethernet:: Executing Ethernet hardware test.')
        # update ip address if requested
        if configure_ip_address:
            if not self.configure_ip_address(ip_address):
                return False
        # execute ping command
        command = ['ping', '-c', '4', '-I', 'eth0', ip_address]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        # verify 0% packet loss
        match = re.search(r'(\d+)% packet loss', str(stdout))
        # TODO verify stderr
        _LOGGER.debug(' '.join(command))
        _LOGGER.debug('\n\t'.join([str(i) for i in stdout.split(b'\n')]))
        if match:
            _LOGGER.info('LDBoardTest::test_ethernet:: Ping had {}% packet loss'
                         .format(match.group(1)))
            if match.group(1) == '0':
                return True
        # if no match or error in call, fail
        _LOGGER.warning('LDBoardTest::test_ethernet:: Packets lost. Test failed.')
        return False

    def test_modbus(self, num_ports=3):
        """
        Test the RS485 modbus connection

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::test_modbus:: Testing modbus register read.')
        # forming ModBus request
        slave, function, start, num = 0, 4, 30003, 1
        global _THREAD_READ_INDEX
        _THREAD_READ_INDEX = -1
        # create thread
        mb_write = ExecuteModBusThread(slave, start, num_ports)
        # begin read sequence
        # create ModBus request
        request = pack('>bbhh', slave, function, start, num).hex()
        req_string = [request[n:n + 2] for n in range(len(request))[::2]]
        # format for LD bootloader `modbustest` output (all ports 1,2,3)
        regex = [''.join(["{{p{}:{}}}".format(i, v) for v in req_string]) for i in range(1, 4)]
        # Initialize readline timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        # send listening command
        self.__serial.send_command(b'modbustest\r\n')
        # start
        mb_write.start()
        # start thread by setting index to 0
        _THREAD_READ_INDEX = 0
        # start timer for 5 seconds
        signal.alarm(5)
        try:
            while _THREAD_READ_INDEX < num_ports:
                # read comm line
                response = self.__serial.read_line()
                # cancel timeout
                signal.alarm(0)
                # TODO if with Mux, regex[thread_read_index]
                # compare against regex created above
                modbus_match = re.search(regex[0], str(response))
                if modbus_match:
                    _LOGGER.info("LDBoardTest::test_modbus:: Port #{} test successful."
                                 .format(_THREAD_READ_INDEX + 1))
                    _THREAD_READ_INDEX += 1
                # checking if `ok\r\n` returned
                ok_match = re.search(r'ok\\r\\n', str(response))
                if ok_match:
                    # send listening commmand again
                    self.__serial.send_command(b'modbustest\r\n')
            # cancel timer
            signal.alarm(0)
        except TimeoutException:
            _LOGGER.warning('LDBoardTest::test_modbus:: Timeout. Test failed.')
            _THREAD_READ_INDEX = num_ports + 1
        # wait
        try:
            mb_write.join()
        except Exception as e:
            _LOGGER.debug('Caught: {}'.format(e))
        self.__serial.reset_input_buffer()
        # success iff equal
        return _THREAD_READ_INDEX == num_ports

    def test_startup_sequence(self):
        """
        Test internal UART, MRAM status from board reset.
        """
        _LOGGER.info('LDBoardTester::test_startup_sequence:: Testing startup sequence.')
        _LOGGER.info('LDBoardTester::test_startup_sequence:: Sending `reset` command.')
        response = self.__serial.read_stop(b'reset\r\n', r'User prgm is not valid', timeout=15)
        match_mram = re.search(r'(?:Mram Test: )(\d+)(?://)(\d+)', str(response))
        if not match_mram:
            _LOGGER.info('LDBoardTester::test_startup_sequence:: Nonconforming `mram` response.')
            return False
        else:
            actual, max = match_mram.group(1), match_mram.group(2)
            _LOGGER.info('LDBoardTester::test_startup_sequence:: mram {}/{}.'.format(actual, max))
            if not actual == max:
                _LOGGER.info('LDBoardTester::test_startup_sequence:: mram failed.')
                return False
        match_uart1 = re.search(r'(?:Testing duart1: \d+{lc:0} passed)', str(response))
        match_uart2 = re.search(r'(?:Testing duart2: \d+{lc:0} passed)', str(response))
        if not match_uart1:
            _LOGGER.info('LDBoardTester::test_startup_sequence:: UART1 failed validation.')
            return False
        if not match_uart2:
            _LOGGER.info('LDBoardTester::test_startup_sequence:: UART2 failed validation.')
            return False
        _LOGGER.info('LDBoardTester::test_startup_sequence:: UART 1 & 2 passed.')
        return True

    def test_voltage(self):
        """
        Test internal voltage is within allowed voltage range.
        """
        _LOGGER.info('LDBoardTester::test_voltage:: Testing 15v supply.')
        response = self.__serial.read_stop(b'15v\r\n', regex=r'15V Supply:')
        # 15V Supply: 15.1V\r\n
        match = re.search(r'(?:15V Supply: )(\d+(?:\.\d+)?)', str(response))
        if match:
            voltage = float(match.group(1))
            _LOGGER.info('LDBoardTester::test_voltage:: Voltage is {} V'.format(voltage))
            if abs(15 - voltage) < 0.5:
                _LOGGER.info('LDBoardTester::test_voltage:: Test passed. Within 500 mV.')
                return True
        _LOGGER.info('LDBoardTester::test_voltage:: Test failed. Not within 500 mV.')
        return False

    def test_datetime_set(self):
        """
        Test the clock setting mechanism. Best if done initially and checking the time later.
        """
        self.__date_set = datetime.datetime.today()
        # date 01/01/17
        date = b'date '
        date += bytearray(self.__date_set.strftime("%x"), 'utf8')
        date += b'\r\n'
        # time 12:00:00
        time = b'time '
        time += bytearray(self.__date_set.strftime("%X"), 'utf8')
        time += b'\r\n'
        _LOGGER.info("LDBoardTester::test_datetime_set:: Testing datetime setting.")
        # TODO sends first three characters if enacted imm. after test startup
        self.__serial.read_stop(date, regex=r'ok')
        self.__serial.read_stop(time, regex=r'ok')
        # implies regex succeeded
        return True

    def test_datetime_read(self):
        """
        Test the clock read mechanism.
        """
        # Response should be 01/01/17 12:00:00
        if not self.__date_set:
            raise OperationsOutOfOrderException
        _LOGGER.info("LDBoardTester::test_datetime_read:: Testing datetime reading.")
        now = datetime.datetime.now()
        result = self.__serial.read_stop(b'time\r\n', regex=self.__date_set.strftime("%x"))
        # regex: 01/01/17 12:00:00
        match = re.search(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})', str(result))
        if match:
            time, date = match.group(1), match.group(2)
            _LOGGER.info("LDBoardTester::test_datetime_read:: Read datetime as {} {}"
                         .format(date, time))
            _LOGGER.info("LDBoardTester::test_datetime_read:: Current datetime is {}"
                         .format(datetime.datetime.now().strftime("%X %x")))
            # parse datetime
            dt = datetime.datetime.strptime("{} {}".format(date, time), "%X %x")
            elapsed = dt - now
            _LOGGER.info("LDBoardTester::test_datetime_read:: Time delta is {} sec"
                         .format(abs(elapsed.total_seconds())))
            # seconds allowed to be off by
            allowance = 5
            if abs(elapsed.total_seconds()) >= allowance:
                _LOGGER.info("LDBoardTester::test_datetime_read:: Failure. Time difference is "
                             "greater than {} seconds.".format(allowance))
                return False
            # else
            _LOGGER.info("LDBoardTester::test_datetime_read:: Passed. Delta <= {} sec"
                         .format(allowance))
            return True
        else:
            _LOGGER.info("LDBoardTester::test_datetime_read:: Expecting "
                         "(\d{{2}}/\d{{2}}/\d{{2}})\s+(\d{{2}}:\d{{2}}:\d{{2}}) got {}"
                         .format(str(result)))
            return False
