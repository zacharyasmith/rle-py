from components.Exceptions import OperationsOutOfOrderException, TimeoutException
from components.Serial import Serial
from components.ModBus import ModBus
import re
import datetime
from struct import pack, unpack
from time import sleep
import threading
import signal
import logging

logger = logging.getLogger()

# used as shared variable between threads
thread_read_index = -1


def _timeout(signum, frame):
    raise TimeoutException('Timeout.')


class ExecuteModBusThread(threading.Thread):
    def __init__(self, slave, start, num_ports):
        threading.Thread.__init__(self)
        logger.debug('ExecuteModBusThread:: Creating thread.')
        self.__serial_modbus = ModBus("serial", device_file='/dev/ttyUSB0', timeout=0)
        self.__slave = slave
        self.__start = start
        self.__num_ports = num_ports

    def __del__(self):
        self.__serial_modbus.close()

    def run(self):
        global thread_read_index
        # wait for listener
        while thread_read_index < 0:
            pass
        while thread_read_index < self.__num_ports:
            # write at 10hz
            sleep(0.1)
            # TODO switch Mux to thread_read_index
            # send command
            self.__serial_modbus.read_input_registers(self.__start, unit=self.__slave)


class LDBoardTester:
    __serial = None
    __date_set = None

    def __init__(self):
        self.__serial = Serial('/dev/ttyUSB1')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__serial.close()

    def test_modbus(self, num_ports=3):
        """
        Test the RS485 modbus connection
        :return: Boolean success
        """
        logger.info('LDBoardTest::test_modbus:: Testing modbus register read.')
        # forming ModBus request
        slave, function, start, num = 0, 4, 30003, 1
        global thread_read_index
        thread_read_index = -1
        # create thread
        mb_write = ExecuteModBusThread(slave, start, num_ports)
        # begin read sequence
        # create ModBus request
        request = pack('>bbhh', slave, function, start, num).hex()
        req_string = [request[n:n + 2] for n in range(len(request))[::2]]
        # format for LD bootloader `modbustest` output (all ports 1,2,3)
        regex = [''.join(["{{p{}:{}}}".format(i, v) for v in req_string]) for i in range(1, 4)]
        # Initialize readline timeout
        signal.signal(signal.SIGALRM, _timeout)
        # send listening commmand
        self.__serial.send_command(b'modbustest\r\n')
        # start
        mb_write.start()
        # start thread by setting index to 0
        thread_read_index = 0
        # start timer for 5 seconds
        signal.alarm(5)
        try:
            while thread_read_index < num_ports:
                # read comm line
                response = self.__serial.read_line()
                # cancel timeout
                signal.alarm(0)
                # TODO if with Mux, regex[thread_read_index]
                # compare against regex created above
                modbus_match = re.search(regex[0], str(response))
                if modbus_match:
                    logger.info("LDBoardTest::test_modbus:: Port #{} test successful.".format(thread_read_index + 1))
                    thread_read_index += 1
                # checking if `ok\r\n` returned
                ok_match = re.search(r'ok\\r\\n', str(response))
                if ok_match:
                    # send listening commmand again
                    self.__serial.send_command(b'modbustest\r\n')
            # cancel timer
            signal.alarm(0)
        except TimeoutException:
            logger.warning('LDBoardTest::test_modbus:: Timeout. Test failed.')
            thread_read_index = num_ports + 1
        # wait
        try:
            mb_write.join()
        except Exception as e:
            logger.debug('Caught:', e)
        # success iff equal
        return thread_read_index == num_ports

    def test_startup_sequence(self):
        """
        Test internal UART, MRAM status from board reset.
        """
        logger.info('LDBoardTester::test_startup_sequence:: Testing startup sequence.')
        logger.info('LDBoardTester::test_startup_sequence:: Sending `reset` command.')
        response = self.__serial.read_stop(b'reset\r\n', r'User prgm is not valid', timeout=15)
        match_mram = re.search(r'(?:Mram Test: )(\d+)(?://)(\d+)', str(response))
        if not match_mram:
            logger.info('LDBoardTester::test_startup_sequence:: Nonconforming `mram` response.')
            return False
        else:
            actual, max = match_mram.group(1), match_mram.group(2)
            logger.info('LDBoardTester::test_startup_sequence:: mram {}/{}.'.format(actual, max))
            if not actual == max:
                logger.info('LDBoardTester::test_startup_sequence:: mram failed.')
                return False
        match_uart1 = re.search(r'(?:Testing duart1: \d+{lc:0} passed)', str(response))
        match_uart2 = re.search(r'(?:Testing duart2: \d+{lc:0} passed)', str(response))
        if not match_uart1:
            logger.info('LDBoardTester::test_startup_sequence:: UART1 failed validation.')
            return False
        if not match_uart2:
            logger.info('LDBoardTester::test_startup_sequence:: UART2 failed validation.')
            return False
        logger.info('LDBoardTester::test_startup_sequence:: UART 1 & 2 passed.')
        return True

    def test_voltage(self):
        """
        Test internal voltage is within allowed voltage range.
        """
        logger.info('LDBoardTester::test_voltage:: Testing 15v supply.')
        response = self.__serial.read_stop(b'15v\r\n', regex=r'15V Supply:')
        # 15V Supply: 15.1V\r\n
        match = re.search(r'(?:15V Supply: )(\d+(?:\.\d+)?)', str(response))
        if match:
            voltage = float(match.group(1))
            logger.info('LDBoardTester::test_voltage:: Voltage is {} V'.format(voltage))
            if abs(15 - voltage) < 0.5:
                logger.info('LDBoardTester::test_voltage:: Test passed. Within 500 mV.')
                return True
        logger.info('LDBoardTester::test_voltage:: Test failed. Not within 500 mV.')
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
        logger.info("LDBoardTester::test_datetime_set:: Testing datetime setting.")
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
        logger.info("LDBoardTester::test_datetime_read:: Testing datetime reading.")
        now = datetime.datetime.now()
        result = self.__serial.read_stop(b'time\r\n', regex=self.__date_set.strftime("%x"))
        # regex: 01/01/17 12:00:00
        match = re.search(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})', str(result))
        if match:
            time, date = match.group(1), match.group(2)
            logger.info("LDBoardTester::test_datetime_read:: Read datetime as {} {}".format(date, time))
            logger.info("LDBoardTester::test_datetime_read:: Current datetime is {}".format(datetime.datetime
                                                                                            .now().strftime("%X %x")))
            # parse datetime
            dt = datetime.datetime.strptime("{} {}".format(date, time), "%X %x")
            elapsed = dt - now
            logger.info("LDBoardTester::test_datetime_read:: Time delta is {} sec".format(abs(elapsed.total_seconds())))
            # seconds allowed to be off by
            allowance = 5
            if abs(elapsed.total_seconds()) >= allowance:
                logger.info("LDBoardTester::test_datetime_read:: Failure. Time difference is greater than "
                            "{} seconds.".format(allowance))
                return False
            # else
            logger.info("LDBoardTester::test_datetime_read:: Passed. Delta <= {} sec".format(allowance))
            return True
        else:
            logger.info("LDBoardTester::test_datetime_read:: Expecting (\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2}) got"
                        " {}".format(str(result)))
            return False

