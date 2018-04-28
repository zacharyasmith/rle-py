"""
components/LDBoardTester.py

Author:
    Zachary Smith
"""
import datetime
import logging
import re
import subprocess
from time import sleep

from components.Exceptions import OperationsOutOfOrderException, TimeoutException
from components.ModBus import ModBus
from components.Serial import Serial
from components.GPIO import GPIO
from components.ADC import read as adc_read, read_diff as adc_read_diff

_LOGGER = logging.getLogger()


class LDBoardTester(object):
    """
    Class for testing the leak detection boards.
    """
    __serial = None
    __date_set = None
    LD2100 = "LD2100"
    LD5200 = "LD5200"
    ip_addresses = ['10.0.0.188', '10.0.0.189', '10.0.0.190', '10.0.0.191', '10.0.0.192', '10.0.0.193']

    def __init__(self, gpio: GPIO):
        """
        Constructor
        """
        self.__gpio = gpio

    def __enter__(self):
        """
        Entry
        Returns:
            self
        """
        self.__serial = Serial('/dev/rleRS232')
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

    def connect_serial(self, mac=None) -> bool:
        _LOGGER.info('LDBoardTest::connect_serial:: Connecting RS232.')
        self.__serial = Serial('/dev/rleRS232')
        if self.__serial and mac:
            _LOGGER.info('LDBoardTest::connect_serial:: Writing MAC address {} (failure raises exception)'.format(mac))
            self.__serial.send_command(bytes('mac ' + mac + '\n', 'utf-8'))
            sleep(10)
            self.__serial._verify_connection(7)
        return True

    def _relay_helper(self, cmd: tuple, expected: tuple, what='all') -> bool:
        for c in cmd:
            self.__serial.read_stop(c, r'ok')
            sleep(.1)
        val = self.__gpio.read(what)
        _LOGGER.info('LDBoardTest::_relay_helper:: Issue {}; exp {}; rcv {}'
                      .format(cmd, expected, val))
        return expected == val

    def test_relay(self, board: str) -> bool:
        """
        Tests the onboard relays

        Args:
            board: the board type

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::test_relay:: Executing relay test.')
        passing = True
        if board == LDBoardTester.LD2100:
            # I0 connected to NC
            # I1 connected to NO
            # LD2100 tested by confirming switchin
            if not self._relay_helper((b'rly1on\n',), (0, 1), 'first2'):
                _LOGGER.error('LDBoardTest::test_relay:: LD2100 on state failed.')
                passing = False
            if not self._relay_helper((b'rly1off\n',), (1, 0), 'first2'):
                _LOGGER.error('LDBoardTest::test_relay:: LD2100 off state failed.')
                passing = False
        else:
            if not self._relay_helper((b'rly6off\n', b'rly4off\n', b'rly5off\n'), (1, 1, 0, 0)):
                _LOGGER.error('LDBoardTest::test_relay:: Some NO has issues disconnecting.')
                passing = False
            if not self._relay_helper((b'rly5on\n',), (1, 0), 'last2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #1 (5) cannot engage.')
                passing = False
            if not self._relay_helper((b'rly4on\n', b'rly5off\n'), (1, 1), 'last2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #2 (4) cannot engage.')
                passing = False
            if not self._relay_helper((b'rly6on\n', b'rly4off\n'), (1, 1), 'last2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #3 (6) cannot engage.')
                passing = False
            if not self._relay_helper((b'rly4on\n', b'rly5on\n'), (0, 0, 1, 1)):
                _LOGGER.error('LDBoardTest::test_relay:: Some NC has issues disconnecting.')
                passing = False
            if not self._relay_helper((b'rly5off\n',), (1, 0), 'first2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #1 (5) cannot disengage.')
                passing = False
            if not self._relay_helper((b'rly4off\n', b'rly5on\n'), (1, 1), 'first2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #2 (4) cannot disengage.')
                passing = False
            if not self._relay_helper((b'rly6off\n', b'rly4on\n'), (1, 1), 'first2'):
                _LOGGER.error('LDBoardTest::test_relay:: Relay #3 (6) cannot disengage.')
                passing = False
            # final disengages
            if not self._relay_helper((b'rly6off\n', b'rly4off\n', b'rly5off\n'), (1, 1, 0, 0)):
                _LOGGER.error('LDBoardTest::test_relay:: Some NO has issues disconnecting. (2)')
                passing = False
        return passing


    def test_led(self, board: str) -> bool:
        """
        Tests the onboard LED

        Args:
            board: the board type

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::test_led:: Executing LED test.')
        # response = self.__serial.send_command(b'reset\n')
        # sleep(3)
        tolerance = 10 / 100    # percent
        expected = .39 if board == LDBoardTester.LD5200 else .39
        tolerance = tolerance * expected
        val = adc_read(3, gain=2)
        # sleep(14)
        _LOGGER.info('LDBoardTest::test_led:: Read {} V.'.format(val))
        if not ((expected - tolerance) <= val <= (expected + tolerance)):
            _LOGGER.info('LDBoardTest::test_led:: Not within tolerance.')
            return False
        return True

    def output_current(self) -> bool:
        """
        Tests the onboard 4-10mA output (LD5200 only)

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::output_current:: Executing output current test.')
        tolerance = 10 / 100    # percent
        resistance = 100    # ohms
        passing = True
        for a in [4, 8, 12, 20, 0]:
            _LOGGER.info('LDBoardTest::output_current:: Testing output current {} mA'.format(a))
            self.__serial.send_command(b'dac ' + str(a).encode('ascii') + b'\n')
            volts = a * 1e-3 * resistance
            tol = tolerance * volts
            val = adc_read_diff(2)
            _LOGGER.info('LDBoardTest::output_current:: Expected {} V, Got {} V'.format(volts, val))
            if not ((volts - tol) <= val <= (volts + tol)):
                _LOGGER.error('LDBoardTest::output_current:: Not within tolerance'.format(a))
                passing = False
        return passing

    def configure_ip_address(self, ip_address: str) -> bool:
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

    def test_ethernet(self, ip_address='10.0.0.188', configure_ip_address=False) -> bool:
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

    def __adc_read(self) -> tuple:
        """
        Internal function. Execute adc1 command and read back

        Returns:
            Tuple (leg1, leg2, leak) or false
        """
        _LOGGER.debug('LDBoardTest::__adc_read:: Reading boards ADC.')
        response = self.__serial.read_stop(b'adc1\n', 'ok', timeout=10)
        response = str(response)
        i = response.find('external cable')
        if i == -1:
            return False
        response = response[i:len(response)]
        match_leg1 = re.search(r'(?:leg1 resistance \(ohms\): )(\d+)', response)
        if not match_leg1:
            return False
        leg1 = match_leg1.group(1)
        match_leg2 = re.search(r'(?:leg2 resistance \(ohms\): )(\d+)', response)
        if not match_leg2:
            return False
        leg2 = match_leg2.group(1)
        match_leak = re.search(r'(?:distance \(ohms\): )(\d+)', response)
        if not match_leak:
            return False
        leak = match_leak.group(1)
        return int(leg1), int(leg2), int(leak)

    def test_length_detector(self, board: str) -> bool:
        """
        Test utilizing length emulator.

        Args:
            board: board type selector

        Returns:
             Boolean success
        """
        _LOGGER.info('LDBoardTest::test_length_detector:: Executing length detector test.')
        sel = 0
        tolerance = 5 / 100  # percent
        passing = True
        # Disengaging short emulator
        self.__gpio.stage(GPIO.SHORT_EMULATOR, 0)
        self.__gpio.commit()
        test_values = [0, 1500, 7100] if board == LDBoardTester.LD2100 else [0, 1500, 7100, 14778, 22067, 29502]
        for r in test_values:    # selected with truth table values
            self.__gpio.stage(GPIO.LENGTH_EMULATOR, sel)
            self.__gpio.commit()
            _LOGGER.info('LDBoardTest::test_length_detector:: Expecting {} ohms'.format(r))
            result = self.__adc_read()
            if not result:
                _LOGGER.error('LDBoardTest::test_length_detector:: Issue getting leak cable results.')
                return False
            _LOGGER.info('LDBoardTest::test_length_detector:: Read {} and {} ohms'.format(result[0], result[1]))
            range = r * tolerance
            if (r - range) > result[0] or (r + range) < result[0]:
                _LOGGER.error('LDBoardTest::test_length_detector:: Loop1 detector not within tolerance.')
                passing = False
            if (r - range) > result[1] or (r + range) < result[1]:
                _LOGGER.error('LDBoardTest::test_length_detector:: Loop2 detector not within tolerance.')
                passing = False
            # next GPIO configuration
            sel += 1
        # Disengaging short emulator
        self.__gpio.stage(GPIO.LENGTH_EMULATOR, 7)
        self.__gpio.commit()
        return passing

    def test_short_detector(self, board: str) -> bool:
        """
        Test utilizing cable short emulator.

        Args:
            board: board selector

        Returns:
             Boolean success
        """
        _LOGGER.info('LDBoardTest::short_length_detector:: Executing short detector test.')
        sel = 2 if board == LDBoardTester.LD2100 else 0
        tolerance = 25 / 100  # percent
        passing = True
        # Disengaging length emulator
        self.__gpio.stage(GPIO.LENGTH_EMULATOR, 6)
        self.__gpio.commit()
        test_values = [14557, 7061, 1468, 0] if board == LDBoardTester.LD2100 else [29459, 21982, 14557, 7061, 1468, 0]
        for r in test_values:    # selected with truth table values
            self.__gpio.stage(GPIO.SHORT_EMULATOR, sel)
            self.__gpio.commit()
            sleep(1)
            _LOGGER.info('LDBoardTest::short_length_detector:: Expecting {} ohms'.format(r))
            result = self.__adc_read()
            if not result:
                _LOGGER.error('LDBoardTest::short_length_detector:: Issue getting short cable results.')
                return False
            _LOGGER.info('LDBoardTest::short_lengh_detector:: Read {} ohms'.format(result[2]))
            range = r * tolerance
            if (r - range) > result[2] or (r + range) < result[2]:
                if not (r == 0 and result[2] < 300):
                    _LOGGER.error('LDBoardTest::short_length_detector:: Leak detector not within tolerance.')
                    passing = False
            # next GPIO configuration
            sel += 1
        # break test
        self.__gpio.stage(GPIO.LENGTH_EMULATOR, 7)
        self.__gpio.stage(GPIO.SHORT_EMULATOR, 7)
        self.__gpio.commit()
        result = self.__adc_read()
        _LOGGER.info('LDBoardTest::short_length_detector:: Executing break test.')
        _LOGGER.info('LDBoardTest::short_length_detector:: Read {}, {}'.format(result[0], result[1]))
        break_test = 24927 if board == LDBoardTester.LD2100 else 40731
        if not (break_test - 20 <= result[0] <= break_test + 20) and (break_test - 20 <= result[1] <= break_test + 20):
            _LOGGER.error('LDBoardTest::short_length_detector:: Break detector failed.')
            passing = False
        return passing

    def test_modbus(self, board) -> bool:
        """
        Test the RS485 modbus connection

        Args:
            board: String LD5200 | LD2100

        Returns:
            Boolean success
        """
        _LOGGER.info('LDBoardTest::test_modbus:: Testing modbus register read for `{}`.'.format(board))
        # forming ModBus request
        slave, start = 254, 9998
        # create modbus client
        serial_modbus = ModBus(device_file='/dev/rleRS485', timeout=1)
        # quick test if is LD2100
        if board == self.LD2100:
            response = serial_modbus.read_holding_registers(start, 1, slave)
            if response:
                return response.registers[0] == 1234
            return False
        # modbustest through serial port
        self.__serial.send_command(b'modbustest\n')
        # listener
        port = 0
        strike = 0
        failing = 3
        try:
            while port < 3:
                # see that modbustest is still active
                # stage change to port
                self.__gpio.stage(GPIO.RS485, port)
                self.__gpio.commit()
                sleep(.1)
                # three strikes and continue
                if strike == 3:
                    strike = 0
                    port += 1
                    continue
                # execute read
                modbus = serial_modbus.read_holding_registers(start, 1, slave)
                if not modbus:
                    _LOGGER.debug('LDBoardTest::test_modbus:: Nothing returned from register read.')
                    strike += 1
                    continue
                # check response
                success = False
                _LOGGER.debug('LDBoardTest::test_modbus:: Read {} for port {}.'.format(modbus.registers[0], port))
                if port == 0:
                    if modbus.registers[0] == 1111:
                        success = True
                elif port == 1:
                    if modbus.registers[0] == 2222:
                        success = True
                elif port == 2:
                    if modbus.registers[0] == 3333:
                        success = True
                if success:
                    _LOGGER.info('LDBoardTest::test_modbus:: Communicated successfully with port {}'.format(port))
                    port += 1
                    failing -= 1
                else:
                    strike += 1
        finally:
            # send ctrl-c to cancel just in case
            self.__serial.send_command(b'\x03\n')
            self.__serial.reset_input_buffer()
        _LOGGER.info("LDBoardTest::test_modbus:: Failed {} test(s)".format(failing))
        return failing == 0

    def test_startup_sequence(self, board=LD5200):
        """
        Test internal UART, MRAM status from board reset.

        Args:
            board: LD5200 or LD2100
        """
        _LOGGER.info('LDBoardTester::test_startup_sequence:: Testing startup sequence.')
        _LOGGER.info('LDBoardTester::test_startup_sequence:: Sending `reset` command.')
        try:
            response = self.__serial.read_stop(b'reset\n', r'User prgm is not valid', timeout=20)
        except TimeoutException:
            _LOGGER.error('LDBoardTester::test_startup_sequence:: Did not reboot within timeout...')
            return False
        if board == LDBoardTester.LD2100:
            return True
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
        response = self.__serial.read_stop(b'15v\n', regex=r'15V Supply:')
        # 15V Supply: 15.1V\n
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
        date += bytearray(self.__date_set.strftime("%m/%d/%y"), 'utf8')
        date += b'\n'
        # time 12:00:00
        time = b'time '
        time += bytearray(self.__date_set.strftime("%H:%M:%S"), 'utf8')
        time += b'\n'
        _LOGGER.info("LDBoardTester::test_datetime_set:: Testing datetime setting.")
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
        result =  self.__serial.read_stop(b'time\n', r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})')
        count = 0
        # regex: 01/01/17 12:00:00
        match = re.search(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2}:\d{2})', str(result))
        if match:
            time, date = match.group(1), match.group(2)
            _LOGGER.info("LDBoardTester::test_datetime_read:: Read datetime as {} {}"
                         .format(date, time))
            _LOGGER.info("LDBoardTester::test_datetime_read:: Current datetime is {}"
                         .format(datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")))
            # parse datetime
            dt = datetime.datetime.strptime("{} {}".format(date, time), "%H:%M:%S %m/%d/%y")
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
        _LOGGER.error("LDBoardTester::test_datetime_read:: Expecting form "
                     "(\d{{2}}/\d{{2}}/\d{{2}})\s+(\d{{2}}:\d{{2}}:\d{{2}})"
                     .format(str(result)))
        return False
