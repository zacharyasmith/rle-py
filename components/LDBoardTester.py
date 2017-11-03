from components.Exceptions import OperationsOutOfOrderException
from components.Serial import Serial
from components.ModBus import ModBus
import re
import datetime
from struct import pack, unpack
from time import sleep


class LDBoardTester:
    __serial = None
    __serial_modbus = None
    __date_set = None

    def __init__(self):
        self.__serial = Serial('/dev/ttyUSB1')
        self.__serial_modbus = ModBus("serial", device_file='/dev/ttyUSB0')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__serial.close()
        self.__serial_modbus.close()

    def test_modbus(self):
        """
        Test the RS485 modbus connection
        :return: Boolean success
        """
        print('LDBoardTest::test_modbus:: Testing modbus register read.')
        # create ModBus request
        slave, function, start, num = 0, 4, 30003, 1
        request = pack('>bbhh', slave, function, start, num).hex()
        req_string = [request[n:n + 2] for n in range(len(request))[::2]]
        # format for LD bootloader `mdobustest` output (all ports 1,2,3)
        regex = [''.join(["{{p{}:{}}}".format(i, v) for v in req_hex]) for i in range(1,4)]
        # TODO read response async and return
        # send command
        self.__serial_modbus.read_input_registers(start, unit=slave)

    def test_startup_sequence(self):
        """
        Test internal UART status from board reset.
        """
        print('LDBoardTester::test_startup_sequence:: Testing startup sequence.')
        print('LDBoardTester::test_startup_sequence:: Sending `reset` command.')
        response = self.__serial.read_stop(b'reset\r\n', r'User prgm is not valid', timeout=15)
        match_mram = re.search(r'(?:Mram Test: )(\d+)(?://)(\d+)', str(response))
        if not match_mram:
            print('LDBoardTester::test_startup_sequence:: Nonconforming `mram` response.')
            return False
        else:
            actual, max = match_mram.group(1), match_mram.group(2)
            print('LDBoardTester::test_startup_sequence:: mram {}/{}.'.format(actual, max))
            if not actual == max:
                print('LDBoardTester::test_startup_sequence:: mram failed.')
                return False
        match_uart1 = re.search(r'(?:Testing duart1: \d+{lc:0} passed)', str(response))
        match_uart2 = re.search(r'(?:Testing duart2: \d+{lc:0} passed)', str(response))
        if not match_uart1:
            print('LDBoardTester::test_startup_sequence:: UART1 failed validation.')
            return False
        if not match_uart2:
            print('LDBoardTester::test_startup_sequence:: UART2 failed validation.')
            return False
        print('LDBoardTester::test_startup_sequence:: UART 1 & 2 passed.')
        return True

    def test_voltage(self):
        """
        Test internal voltage is within allowed voltage range.
        """
        print('LDBoardTester::test_voltage:: Testing 15v supply.')
        response = self.__serial.read_stop(b'15v\r\n', regex=r'15V Supply:')
        # 15V Supply: 15.1V\r\n
        match = re.search(r'(?:15V Supply: )(\d+(?:\.\d+)?)', str(response))
        if match:
            voltage = float(match.group(1))
            print('LDBoardTester::test_voltage:: Voltage is', voltage)
            if abs(15 - voltage) < 0.5:
                print('LDBoardTester::test_voltage:: Test passed. Within 500 mV.')
                return True
        print('LDBoardTester::test_voltage:: Test failed. Not within 500 mV.')
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
        print("LDBoardTester::test_datetime_set:: Testing datetime setting.")
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
        print("LDBoardTester::test_datetime_read:: Testing datetime reading.")
        now = datetime.datetime.now()
        result = self.__serial.read_stop(b'time\r\n', regex=self.__date_set.strftime("%x"))
        # regex: 01/01/17 12:00:00
        match = re.search(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})', str(result))
        if match:
            time, date = match.group(1), match.group(2)
            print("LDBoardTester::test_datetime_read:: Read datetime as {} {}".format(date, time))
            print("LDBoardTester::test_datetime_read:: Current datetime is {}".format(datetime.datetime.now().
                                                                                      strftime("%X %x")))
            # parse datetime
            dt = datetime.datetime.strptime("{} {}".format(date, time), "%X %x")
            elapsed = dt - now
            print("LDBoardTester::test_datetime_read:: Time delta is", abs(elapsed.total_seconds()), 'sec')
            # seconds allowed to be off by
            allowance = 5
            if abs(elapsed.total_seconds()) >= allowance:
                print("LDBoardTester::test_datetime_read:: Failure. Time difference is greater than {} seconds."
                      .format(allowance))
                return False
            # else
            print("LDBoardTester::test_datetime_read:: Passed. Delta <= {} sec".format(allowance))
            return True
        else:
            print("LDBoardTester::test_datetime_read:: Expecting (\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2}) got ",
                  str(result))
            return False

