"""
components/GPIO.py

Author:
    Zachary Smith
"""
import logging

_LOGGER = logging.getLogger()

try:
    import RPi.GPIO as _gpio
except RuntimeError:
    _LOGGER.error("Critical: Library `RPi.GPIO` could not be imported. Try running as Admin.")
    exit(1)


def int_to_bin(num):
    """
    Function to convert number to binary state
    Args:
        num: int

    Returns:
        list of binary states from LSB to MSB
    """
    ret = []
    # from lsb to msb
    for i in range(0, 5, -1):
        # TODO HERE FIX
        ret.append(_gpio.HIGH if num  else _gpio.LOW)
    return ret


class GPIO(object):
    """
    Class GPIO has methods for setting and reading GPIO states.
    Proprietary for SeaLion configuration.
    """

    # const
    BOARD = 'board'
    EMULATOR = 'emulator'
    RS485 = 'rs485'

    __channel_list = None
    #
    __board_selector = {
        'pins': [3, 5, 7],
        'present_state': tuple(),
        'state': tuple()
    }
    __emulator_selector = {
        'pins': [11, 12, 13, 15, 16],
        'present_state': tuple(),
        'state': tuple()
    }
    __rs485_selector = {
        'pins': [18, 22],
        'present_state': tuple(),
        'state': tuple()
    }

    def __init__(self):
        """
        Initializes internal settings.
        """
        _gpio.setmode(_gpio.BOARD)
        # create channel list as combo of other pin lists
        self.__channel_list = list()
        self.__channel_list.append(self.__board_selector_pins)
        self.__channel_list.append(self.__emulator_selector_pins)
        self.__channel_list.append(self.__rs485_selector_pins)
        # set as outputs and low
        _gpio.setup(self.__channel_list, _gpio.OUT)

    def stage(self, what, state):
        """
        Function to current device IP address based on interface name
        Args:
            what: Select GPIO.(BOARD | EMULATOR | RS485)
            state: int defining binary state of the selector `what`
        """
        gpio_state = int_to_bin(state)
        if what == self.BOARD:
            self.__board_selector['state'] = tuple(gpio_state[:3])
        elif what == self.EMULATOR:
            self.__emulator_selector['state'] = tuple(gpio_state[:4])
        elif what == self.RS485:
            self.__rs485_selector['state'] = tuple(gpio_state[:2])


