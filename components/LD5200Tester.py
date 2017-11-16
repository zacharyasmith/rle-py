from time import sleep
from components.Exceptions import ConnectionRefusalException
from components.LDBoard import LDBoard
from components.LDBoardTester import LDBoardTester
import logging

logger = logging.getLogger()


class LD5200Tester(LDBoard):
    def __init__(self):
        LDBoard.__init__(self)

    def test(self):
        """
        Executes test of board hardware.
        :return: Boolean of board passing
        """
        try:
            with LDBoardTester() as ld:
                self.process_test_result('rs232_connection', True)
                self.process_test_result('datetime_set', ld.test_datetime_set())
                self.process_test_result('startup_sequence', ld.test_startup_sequence())
                self.process_test_result('ps_voltage', ld.test_voltage())
                self.process_test_result('rs485_modbus', ld.test_modbus())
                logger.info('Sleeping for 3 seconds...')
                sleep(3)
                self.process_test_result('datetime_read', ld.test_datetime_read())
        except ConnectionRefusalException:
            logger.info("Connection refused.")
            self.process_test_result('rs232_connection', False)
        return self.passing
