"""
components/LD5200Tester.py

Author:
    Zachary Smith
"""

from time import sleep
import logging

from pymodbus.exceptions import ConnectionException

from components.Exceptions import ConnectionRefusalException
from components.LDBoard import LDBoard
from components.LDBoardTester import LDBoardTester
from serial.serialutil import SerialException
from components.GPIO import GPIO

_LOGGER = logging.getLogger()


class LD5200Tester(LDBoard):
    """
    Inherits from LDBoard. Implements test() function.
    """
    def __init__(self, serial, mac):
        """
        Constructor.
        """
        LDBoard.__init__(self, serial, mac, 'LD5200', LDBoardTester.LD5200)

    def test(self, gpio: GPIO, ip_address: str, args):
        """
        Executes test of board hardware.

        Returns:
            Boolean of board passing
        """
        _LOGGER.info('Executing LD5200 test.\n\tSerial: {}\n\tMAC: {}'.format(self.serial_address, self.mac_address))
        all = args == None or args['all']
        try:
            ld_board = LDBoardTester(gpio)
            if args['rs232'] or all:
                self.process_test_result('rs232_connection', ld_board.connect_serial())
                if all:
                    self.process_test_result('datetime_set', ld_board.test_datetime_set())
                    self.process_test_result('startup_sequence', ld_board.test_startup_sequence())
                    self.process_test_result('ps_voltage', ld_board.test_voltage())
                    self.process_test_result('datetime_read', ld_board.test_datetime_read())
                if args['length'] or all:
                    self.process_test_result('length_detection', ld_board.test_length_detector(LDBoardTester.LD5200))
                if args['short'] or all:
                    self.process_test_result('short_detection', ld_board.test_short_detector(LDBoardTester.LD5200))
                if args['rs485'] or all:
                    self.process_test_result('rs485_modbus', ld_board.test_modbus(LDBoardTester.LD5200))
                if args['eth']or all:
                    self.process_test_result('ethernet_ping',
                                             ld_board.test_ethernet(ip_address, configure_ip_address=True))
                if args['relay'] or all:
                    self.process_test_result('relay_test', ld_board.test_relay(LDBoardTester.LD5200, None))
                if args['current']:
                    self.process_test_result('output_current', ld_board.output_current())
            if args['led'] or all:
                self.process_test_result('led_test', ld_board.test_led(LDBoardTester.LD5200))
        except ConnectionRefusalException:
            _LOGGER.error("RS232 connection refused.")
            self.process_test_result('rs232_connection', False)
        except ConnectionException as e:
            if e.string:
                _LOGGER.error(e.string)
            _LOGGER.error('USB to RS485(ModBus) adapter failed to connect.')
        except SerialException as e:
            if e.strerror:
                _LOGGER.error(e.strerror)
            _LOGGER.error('USB to RS232 adapter failed to connect.')
            self.process_test_result('rs232_connection', False)
        return self.passing
