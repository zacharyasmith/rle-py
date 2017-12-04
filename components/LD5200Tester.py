"""
components/LD5200Tester.py

Author:
    Zachary Smith
"""

from time import sleep
import logging
from components.Exceptions import ConnectionRefusalException
from components.LDBoard import LDBoard
from components.LDBoardTester import LDBoardTester

_LOGGER = logging.getLogger()


class LD5200Tester(LDBoard):
    """
    Inherits from LDBoard. Implements test() function.
    """
    def __init__(self):
        """
        Constructor.
        """
        LDBoard.__init__(self)

    def test(self):
        """
        Executes test of board hardware.

        Returns:
            Boolean of board passing
        """
        try:
            with LDBoardTester() as ld_board:
                # rs232_connection implied by success with __enter__
                self.process_test_result('rs232_connection', result=True)
                self.process_test_result('datetime_set', ld_board.test_datetime_set())
                self.process_test_result('startup_sequence', ld_board.test_startup_sequence())
                self.process_test_result('ps_voltage', ld_board.test_voltage())
                self.process_test_result('rs485_modbus', ld_board.test_modbus())
                self.process_test_result('ethernet_ping',
                                         ld_board.test_ethernet('10.0.0.188',
                                                                configure_ip_address=True))
                _LOGGER.info('Sleeping for 3 seconds...')
                sleep(3)
                self.process_test_result('datetime_read', ld_board.test_datetime_read())
        except ConnectionRefusalException:
            _LOGGER.info("Connection refused.")
            self.process_test_result('rs232_connection', False)
        return self.passing
