"""
components/LD2100Tester.py

Author:
    Zachary Smith
"""

from time import sleep
import logging
from pymodbus.exceptions import ConnectionException
from components.Exceptions import ConnectionRefusalException
from components.LDBoard import LDBoard
from components.LDBoardTester import LDBoardTester
from components.GPIO import GPIO
from serial.serialutil import SerialException

_LOGGER = logging.getLogger()


class LD2100Tester(LDBoard):
    """
    Inherits from LDBoard. Implements test() function.
    """
    def __init__(self, serial, mac):
        """
        Constructor.
        """
        LDBoard.__init__(self, serial, mac, '', '')

    def test(self, gpio: GPIO, ip_address: str, args):
        """
        Executes test of board hardware.

        Returns:
            Boolean of board passing
        """
        _LOGGER.info('Executing LD2100 test.\n\tSerial: {}\n\tMAC: {}'.format(self.serial_address, self.mac_address))
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
                if args['relay'] or all:
                    self.process_test_result('relay_test', ld_board.test_relay(LDBoardTester.LD2100, 'last2' if args['port'] == 4 else 'first2'))
                if args['length'] or all:
                    self.process_test_result('length_detection', ld_board.test_length_detector(LDBoardTester.LD2100))
                if args['short'] or all:
                    self.process_test_result('short_detection', ld_board.test_short_detector(LDBoardTester.LD2100))
                if args['eth']or all:
                    self.process_test_result('ethernet_ping',
                                             ld_board.test_ethernet(ip_address, configure_ip_address=True))
            if args['rs485'] or all:
                # LD5200 3 -> 3
                # LD5200 4 -> 2
                # LD5200 5 -> 1
                if args['port'] == 3:
                    gpio.stage(GPIO.RS485, 2)
                    gpio.commit()
                elif args['port'] == 4:
                    gpio.stage(GPIO.RS485, 1)
                    gpio.commit()
                elif args['port'] == 5:
                    gpio.stage(GPIO.RS485, 0)
                    gpio.commit()
                sleep(.1)
                self.process_test_result('rs485_modbus', ld_board.test_modbus(LDBoardTester.LD2100))
            if args['led'] or all:
                self.process_test_result('led_test', ld_board.test_led())
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
