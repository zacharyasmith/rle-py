"""
view/SeaLionThread.py

Author:
    Zachary Smith
"""

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
import logging
from time import sleep
from datetime import datetime

from pymodbus.exceptions import ConnectionException
from components.Exceptions import ConnectionRefusalException
from serial.serialutil import SerialException

from components.LDBoard import LDBoard
from components.LDBoardTester import LDBoardTester
from components.GPIO import GPIO
from components.IOUtilities import get_log_path

_LOGGER = logging.getLogger()


class WorkerSignals(QObject):
    """
    Defines the signals available to the worker thread.
    """
    finished = pyqtSignal()
    update = pyqtSignal(tuple)
    debug_update = pyqtSignal(tuple)
    alert = pyqtSignal(tuple)
    status_bar = pyqtSignal(str)


class SeaLionThread(QRunnable):
    """
    Worker thread. Executes all tests on LDBoards.
    """
    def __init__(self, gui_instance):
        """
        Constructor

        Args:
            gui_instance: The SeaLionGUI instance
        """
        super(SeaLionThread, self).__init__()
        self.gui = gui_instance
        self.signals = WorkerSignals()

    def __check_signals(self, tray: int) -> bool:
        while self.gui.pause:
            print('Pause ack')
            self.signals.debug_update.emit((tray, "Paused"))
            sleep(0.35)
            self.signals.debug_update.emit((tray, ""))
            sleep(0.35)
            pass
        if self.gui.cancel:
            print('Cancel ack')
            self.signals.debug_update.emit((tray, "Cancelled"))
            self.signals.finished.emit()
            return True
        return False

    """
    Collection of items in gui.objects[i]:
        ['board_type'] = LDBoardTester.LD5200 | LDBoardTests.LD2100
        ['identifier'] = ex: "LD5200_6"
        ['GPIO_address'] = ex: 2
        ['mac'] = mac string
        ['serial'] = serial string
        ['active'] = True (indicate if mac/serial supplied)
        ['test_container'] = LDBoard() instance
        ['log_path'] = path string
        ['tests_total'] = int
        ['tests_finished'] = int
        ['passing'] = bool
        ['ethernet_participate'] = bool
    """
    @pyqtSlot()
    def run(self):
        gui = self.gui
        logging_format = '%(levelname)s::%(message)s'
        if not gui.debug:
            gpio = GPIO()
        else:
            gpio = None
        for i in range(6):
            # check for signals
            if self.__check_signals(i):
                return

            # ensure object is active
            if not gui.objects[i]['active']:
                gui.objects[i]['log_path'] = None
                continue
            curr = gui.objects[i]
            test_container = LDBoard(curr['serial'], curr['mac'],
                                     curr['identifier'], curr['board_type'])
            curr['test_container'] = test_container

            # setup logging
            # writes to logging directory with identifier
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            path = get_log_path(curr['identifier'])
            logging.basicConfig(filename=path, filemode='a', level=logging.INFO,
                                format=logging_format)
            curr['log_path'] = path

            # Info log
            _LOGGER.info('Board/tray: {}'.format(curr['identifier']))
            _LOGGER.info('Serial number: {}'.format(curr['serial']))
            _LOGGER.info('MAC address: {}'.format(curr['mac']))

            # GPIO
            if not gui.debug:
                gpio.stage(GPIO.BOARD, state=curr['GPIO_address'])
                gpio.commit()

            # Setup progress bar
            curr['tests_total'] = 13 if curr['board_type'] == LDBoardTester.LD5200 else 12
            curr['tests_finished'] = 0

            curr['passing'] = True
            curr['ethernet_participate'] = False

            ld_board = LDBoardTester(gpio)
            try:
                # check for signals
                if self.__check_signals(i):
                    return

                # serial connection
                self.signals.debug_update.emit((i, "Writing MAC address"))
                if not gui.debug:
                    result = ld_board.connect_serial(curr['mac'])
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('rs232_connection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Writing MAC address"))
                if not result:
                    continue

                # check for signals
                if self.__check_signals(i):
                    return

                # datetime set
                self.signals.debug_update.emit((i, "Running: Datetime write"))
                if not gui.debug:
                    result = ld_board.test_datetime_set()
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('datetime_set', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Datetime write"))

                # check for signals
                if self.__check_signals(i):
                    return

                # startup sequence
                self.signals.debug_update.emit((i, "Running: Startup sequence test"))
                if not gui.debug:
                    result = ld_board.test_startup_sequence(curr['board_type'])
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('startup_sequence', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Startup sequence test"))

                # check for signals
                if self.__check_signals(i):
                    return

                # power supply voltage
                self.signals.debug_update.emit((i, "Running: Voltage level check"))
                if not gui.debug:
                    result = ld_board.test_voltage()
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('ps_voltage', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Voltage level check"))

                # check for signals
                if self.__check_signals(i):
                    return

                # relay test
                self.signals.debug_update.emit((i, "Running: Relay test"))
                if not gui.debug:
                    # signalling test to use either (I0, I1) or (I2, I3)
                    relays = None
                    if curr['board_type'] == LDBoardTester.LD2100:
                        relays = 'last2' if curr['GPIO_address'] == 4 else 'first2'
                    result = ld_board.test_relay(curr['board_type'], relays)
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('relay_test', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Relay test"))

                # check for signals
                if self.__check_signals(i):
                    return

                # length emulator
                self.signals.debug_update.emit((i, "Running: Cable emulator (length)"))
                if not gui.debug:
                    result = ld_board.test_length_detector(curr['board_type'])
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('length_detection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Cable emulator (length)"))

                # check for signals
                if self.__check_signals(i):
                    return

                # short emulator
                self.signals.debug_update.emit((i, "Running: Cable emulator (short)"))
                if not gui.debug:
                    result = ld_board.test_short_detector(curr['board_type'])
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('short_detection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Cable emulator (short)"))

                # check for signals
                if self.__check_signals(i):
                    return

                # RS485 modbus
                try:
                    self.signals.debug_update.emit((i, "Running: RS485 ModBus"))
                    if not gui.debug:
                        # LD5200 3 -> 3
                        # LD5200 4 -> 2
                        # LD5200 5 -> 1
                        if curr['GPIO_address'] == 3:
                            gpio.stage(GPIO.RS485, 2)
                            gpio.commit()
                        elif curr['GPIO_address'] == 4:
                            gpio.stage(GPIO.RS485, 1)
                            gpio.commit()
                        elif curr['GPIO_address'] == 5:
                            gpio.stage(GPIO.RS485, 0)
                            gpio.commit()
                        sleep(.1)
                        result = ld_board.test_modbus(curr['board_type'])
                    else:
                        result = True
                        sleep(2)
                    test_container.process_test_result('rs485_modbus', result)
                    curr['tests_finished'] += 1
                    curr['passing'] = curr['passing'] and result
                    self.signals.update.emit((i, "Done: RS485 ModBus"))
                except ConnectionException as e:
                    if e.string:
                        _LOGGER.error(e.string)
                    _LOGGER.error('USB to RS485(ModBus) adapter failed to connect.')
                    self.signals.alert.emit(("USB/RS485 Connection Refused",
                                             "Check that no other processes are using"
                                             "it and that it is plugged in."))
                    curr['passing'] = False
                # turn off
                gpio.stage(GPIO.RS485, 3)
                gpio.commit()

                # check for signals
                if self.__check_signals(i):
                    return

                # RS485 ModBus
                self.signals.debug_update.emit((i, "Running: Datetime read"))
                if not gui.debug:
                    result = ld_board.test_datetime_read()
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('datetime_read', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: Datetime read"))

                # check for signals
                if self.__check_signals(i):
                    return

                # write ip address
                self.signals.debug_update.emit((i, "Assigned " + LDBoardTester.ip_addresses[i]))
                if not gui.debug:
                    result = ld_board.configure_ip_address(LDBoardTester.ip_addresses[i])
                else:
                    result = True
                    sleep(2)
                curr['tests_finished'] += 1
                curr['ethernet_participate'] = result
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done writing IP address"))

                # check for signals
                if self.__check_signals(i):
                    return

                # LED test
                self.signals.debug_update.emit((i, "Running: LED test"))
                if not gui.debug:
                    result = ld_board.test_led()
                else:
                    result = True
                    sleep(2)
                test_container.process_test_result('led_test', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done: LED test"))

                # 4-20 mA test
                if curr['board_type'] == LDBoardTester.LD5200:
                    # check for signals
                    if self.__check_signals(i):
                        return

                    self.signals.debug_update.emit((i, "Running: Current source"))
                    if not gui.debug:
                        result = ld_board.output_current()
                    else:
                        result = True
                        sleep(2)
                    test_container.process_test_result('output_current', result)
                    curr['tests_finished'] += 1
                    curr['passing'] = curr['passing'] and result
                    self.signals.update.emit((i, "Done: Current source"))

                self.signals.update.emit((i, "Waiting for others"))
            except ConnectionRefusalException:
                _LOGGER.error("RS232 connection refused.")
                test_container.process_test_result('rs232_connection', False)
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "RS232 connection issue"))
            except SerialException as e:
                if e.strerror:
                    _LOGGER.error(e.strerror)
                _LOGGER.error('USB to RS232 adapter failed to connect.')
                self.signals.alert.emit(("USB/RS232 Connection Refused",
                                         "Check that no other processes are using it."))
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "RS232 connection issue"))
            except OSError as e:
                if e.strerror:
                    _LOGGER.error(e.strerror)
                _LOGGER.error('I2C connection issue. Check wires.')
                self.signals.alert.emit(("I2C Connection Failed", "Check signal wires for ADC."))
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "I2C connection issue"))

        # conduct ethernet tests
        for i in range(6):
            if not gui.objects[i]['active']:
                continue
            if not gui.objects[i]['ethernet_participate']:
                continue
            curr = gui.objects[i]
            test_container = curr['test_container']

            # check for signals
            if self.__check_signals(i):
                return

            # setup logging
            # writes to logging directory with identifier
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            path = curr['log_path']
            logging.basicConfig(filename=path, filemode='a', level=logging.INFO,
                                format=logging_format)

            ld_board = LDBoardTester(gpio)
            # ethernet test
            self.signals.debug_update.emit((i, "Running: Ethernet test"))
            if not gui.debug:
                result = ld_board.test_ethernet(LDBoardTester.ip_addresses[i])
                self.signals.debug_update.emit((i, "Running: Resetting IP to 10.0.0.188"))
                if not ld_board.configure_ip_address('10.0.0.188'):
                    self.signals.debug_update.emit((i, "Error with IP address assignment"))
                    sleep(3)
                    curr['passing'] = False
            else:
                result = True
                sleep(2)
            test_container.process_test_result('ethernet_test', result)
            curr['tests_finished'] += 1
            curr['passing'] = curr['passing'] and result
            self.signals.update.emit((i, "Done: Ethernet test"))

        # signal to GUI
        # process finished
        self.signals.finished.emit()


class TimeUpdater(QRunnable):
    def __init__(self, gui_instance):
        """
        Constructor
        """
        super(TimeUpdater, self).__init__()
        self.signals = WorkerSignals()
        self.gui = gui_instance

    @pyqtSlot()
    def run(self):
        while self.gui.testing:
            sleep(1)
            difference = datetime.now() - self.gui.test_start
            difference = divmod(difference.total_seconds(), 60)
            self.signals.status_bar.emit('{} min {} sec'.format(int(difference[0]),
                                                                int(difference[1])))
        self.signals.status_bar.emit('Done: {} min {} sec'.format(int(difference[0]),
                                                                  int(difference[1])))


