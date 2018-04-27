"""
components/LDBoard.py

Author:
    Zachary Smith
"""
import logging
from collections import OrderedDict

_LOGGER = logging.getLogger()


class LDBoard(object):
    """
    LDBoard class for representing a Lead Detection board by RLE Technologies.
    """
    def __init__(self, serial_address, mac_address, name, type):
        """
        Constructor.
        """
        self.passing = True
        self.test_status = OrderedDict()
        self.serial_address = serial_address
        self.mac_address = mac_address
        self.name = name
        self.type = type

    def results(self):
        """
        Processes test status dictionary in its current state.

        Returns:
            multiline string of test results
        """
        ret_val = 'Passing: {}\n'.format(self.passing)
        for key in self.test_status.keys():
            ret_val += '\t{}: {}\n'.format(key, 'passed' if self.test_status[key] else 'failed')
        return ret_val

    def process_test_result(self, name, result):
        """
        Processes result by updating status dictionary

        Args:
            name: Name of the test
            result: Boolean result
        """
        self.test_status[name] = result
        self.passing = self.passing if result else False
        _LOGGER.info('Test {} resulted: {}'.format(name, 'passed' if result else 'failed'))
