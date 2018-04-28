"""
components/GPIO.py

Author:
    Zachary Smith
"""
import logging
from time import sleep

_LOGGER = logging.getLogger()

try:
    import RPi.GPIO as _gpio
except RuntimeError:
    _LOGGER.error("Critical: Library `RPi.GPIO` could not be imported. Try running as Admin.")
    exit(1)
except ModuleNotFoundError:
    _LOGGER.error("Functionality won't work for GPIO.")


def state_tuple(num):
    """
    Function to convert number to binary state
    Args:
        num: int

    Returns:
        tuple of binary states from LSB to MSB
    """
    ret = []
    for t in [0b100, 0b010, 0b001]:
        ret.append(_gpio.HIGH if (num & t) > 0 else _gpio.LOW)
    return tuple(ret)


class GPIO(object):
    """
    Class GPIO has methods for setting and reading GPIO states.
    Proprietary for SeaLion configuration.
    """

    # const
    BOARD = 'board'
    SHORT_EMULATOR = 'short_emulator'
    LENGTH_EMULATOR = 'length_emulator'
    RS485 = 'rs485'

    __channel_list = None

    # Mapping: functions --> IO ports

    # Truth table
    # C | B | A | Function
    # -------------------------
    # 0   0   0   Tray 4 (LD5200)
    # 0   0   1   Tray 5 (LD5200)
    # 0   1   0   Tray 6 (LD5200)
    # 0   1   1   Tray 1 (LD2100)
    # 1   0   0   Tray 2 (LD2100)
    # 1   0   1   Tray 3 (LD2100)
    # 1   1   0   Unused
    # 1   1   1   Unused
    __board_selector = {
        #        C  B   A
        'pins': [7, 11, 12],
        #          C   B   A
        'pins_2': [31, 32, 33],
        'present_state': tuple(),
        'state': tuple()
    }

    # Truth table
    # C | B | A | Function
    # -------------------------
    # 0   0   0   Short (0ft)
    # 0   0   1   Short (357ft)
    # 0   1   0   Short (714ft)
    # 0   1   1   Short (1070ft)
    # 1   0   0   Short (1425ft)
    # 1   0   1   Short (1785ft)
    # 1   1   0   Open for Loop1
    # 1   1   1   Open for Loop2
    __short_selector = {
        #        C   B   A
        'pins': [13, 15, 16],
        'present_state': tuple(),
        'state': tuple()
    }

    # Truth table
    # C | B | A | Function
    # -------------------------
    # 0   0   0   Length (0ft)
    # 0   0   1   Length (357ft)
    # 0   1   0   Length (714ft)
    # 0   1   1   Length (1070ft)
    # 1   0   0   Length (1425ft)
    # 1   0   1   Length (1785ft)
    # 1   1   0   Open for Loop1
    # 1   1   1   Open for Loop2
    __length_selector = {
        #        C   B   A
        'pins': [18, 19, 21],
        'present_state': tuple(),
        'state': tuple()
    }

    # Truth table
    # C | B | A | Function
    # -------------------------
    # 0   0   0   RS485 port #1
    # 0   0   1   RS485 port #2
    # 0   1   0   RS485 port #3
    # 0   1   1   Unused
    # 1   0   0   Unused
    # 1   0   1   Unused
    # 1   1   0   Unused
    # 1   1   1   Unused
    __rs485_selector = {
        #        C   B   A
        'pins': [22, 23, 24],
        'present_state': tuple(),
        'state': tuple()
    }

    # Inputs for Relay Test
    # Mapping
    _relays = {
        #        I0  I1  I2  I3
        'pins': [35, 36, 37, 38]
    }

    def __init__(self):
        """
        Initializes internal settings.
        """
        _gpio.setmode(_gpio.BOARD)
        # create channel list as combo of other pin lists
        self.__channel_list = list()
        self.__channel_list.extend(self.__board_selector['pins'])
        self.__channel_list.extend(self.__board_selector['pins_2'])
        self.__channel_list.extend(self.__short_selector['pins'])
        self.__channel_list.extend(self.__length_selector['pins'])
        self.__channel_list.extend(self.__rs485_selector['pins'])
        # set as outputs and low
        _gpio.setup(self.__channel_list, _gpio.OUT)
        _gpio.setup(self._relays['pins'], _gpio.IN)
        _gpio.output(self.__channel_list, _gpio.LOW)

    def __del__(self):
        _gpio.cleanup()

    def stage(self, what, state):
        """
        Function to current device IP address based on interface name
        Args:
            what: Select GPIO.(BOARD | SHORT_EMULATOR | LENGTH_EMULATOR | RS485)
            state: int defining binary state of the selector `what` (Check truth tables)
        """
        _LOGGER.debug('GPIO::stage:: Staging {} into state {}.'.format(what, state))
        gpio_state = state_tuple(state)
        if what == self.BOARD:
            self.__board_selector['state'] = gpio_state
        elif what == self.SHORT_EMULATOR:
            self.__short_selector['state'] = gpio_state
        elif what == self.LENGTH_EMULATOR:
            self.__length_selector['state'] = gpio_state
        elif what == self.RS485:
            self.__rs485_selector['state'] = gpio_state

    def commit(self):
        """
        Commits the staged changes in one pass.
        """
        # compare staged state to present
        # only update if not equal
        if self.__board_selector['present_state'] != self.__board_selector['state']:
            _LOGGER.debug('GPIO::commit:: Committing changes on `{}`.'.format('board_selector'))
            # update both pin banks
            _gpio.output(self.__board_selector['pins'], self.__board_selector['state'])
            _gpio.output(self.__board_selector['pins_2'], self.__board_selector['state'])
            self.__board_selector['present_state'] = self.__board_selector['state']

        if self.__short_selector['present_state'] != self.__short_selector['state']:
            _LOGGER.debug('GPIO::commit:: Committing changes on `{}`.'.format('short_selector'))
            _gpio.output(self.__short_selector['pins'], self.__short_selector['state'])
            self.__short_selector['present_state'] = self.__short_selector['state']

        if self.__length_selector['present_state'] != self.__length_selector['state']:
            _LOGGER.debug('GPIO::commit:: Committing changes on `{}`.'.format('length_selector'))
            _gpio.output(self.__length_selector['pins'], self.__length_selector['state'])
            self.__length_selector['present_state'] = self.__length_selector['state']

        if self.__rs485_selector['present_state'] != self.__rs485_selector['state']:
            _LOGGER.debug('GPIO::commit:: Committing changes on `{}`.'.format('rs485_selector'))
            _gpio.output(self.__rs485_selector['pins'], self.__rs485_selector['state'])
            self.__rs485_selector['present_state'] = self.__rs485_selector['state']
        sleep(50 / 1000)    # sleep for 50 ms to let digital circuits settle
        _LOGGER.debug('GPIO::commit:: Done.')

    I0 = 'IO'
    I1 = 'I1'
    I2 = 'I2'
    I3 = 'I3'
    HIGH = _gpio.HIGH
    LOW = _gpio.LOW
    def read(self, what):
        """
        Read directly from the relay inputs I0-I3
        If what == 'first2', a tuple will be returned (I0, I1)
        If what == 'last2', a tuple will be returned (I2, I3)
        If what == 'all', a tuple will be returned (I0, I1, I2, I3)
        """
        val0 = _gpio.input(self._relays['pins'][0])
        val1 = _gpio.input(self._relays['pins'][1])
        val2 = _gpio.input(self._relays['pins'][2])
        val3 = _gpio.input(self._relays['pins'][3])
        if what == self.I0:
            return val0
        elif what == self.I1:
            return val1
        elif what == self.I2:
            return val2
        elif what == self.I3:
            return val3
        if what == 'first2':
            return (val0, val1)
        elif what == 'last2':
            return (val2, val3)
        else:
            return (val0, val1, val2, val3)

if __name__ == "__main__":
    gpio = GPIO()
    gpio.stage(GPIO.BOARD, 3)
    gpio.stage(GPIO.RS485, 1)
    gpio.stage(GPIO.LENGTH_EMULATOR, 5)
    gpio.commit()
    pass
