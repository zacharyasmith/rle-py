"""
view/Worker.py

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
        gpio = GPIO()
        for i in range(6):
            if not gui.objects[i]['active']:
                continue
            curr = gui.objects[i]
            test_container = LDBoard(curr['serial'], curr['mac'], curr['identifier'], curr['board_type'])
            curr['test_container'] = test_container

            # setup logging
            # writes to logging directory with identifier
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            path = get_log_path(curr['identifier'])
            logging.basicConfig(filename=path, filemode='a', level=logging.DEBUG,
                                format='{} - %(levelname)s - %(message)s'.format(curr['identifier']))
            curr['log_path'] = path

            # GPIO
            gpio.stage(GPIO.BOARD, state=curr['GPIO_address'])
            gpio.commit()

            # Setup progress bar
            curr['tests_total'] = 12 if curr['board_type'] == LDBoardTester.LD5200 else 11
            curr['tests_finished'] = 0

            curr['passing'] = True
            curr['ethernet_participate'] = False

            ld_board = LDBoardTester(gpio)
            try:
                # serial connection
                self.signals.debug_update.emit((i, "Writing MAC address"))
                result = ld_board.connect_serial(curr['mac'])
                # result = True
                # sleep(2)
                test_container.process_test_result('rs232_connection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))
                if not result:
                    continue

                # datetime set
                self.signals.debug_update.emit((i, "Running: Datetime write"))
                result = ld_board.test_datetime_set()
                # result = True
                # sleep(2)
                test_container.process_test_result('datetime_set', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # startup sequence
                self.signals.debug_update.emit((i, "Running: Startup sequence test"))
                result = ld_board.test_startup_sequence(curr['board_type'])
                # result = True
                # sleep(2)
                test_container.process_test_result('startup_sequence', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # power supply voltage
                self.signals.debug_update.emit((i, "Running: Voltage level check"))
                result = ld_board.test_voltage()
                # result = True
                # sleep(2)
                test_container.process_test_result('ps_voltage', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # length emulator
                self.signals.debug_update.emit((i, "Running: Cable emulator (length)"))
                result = ld_board.test_length_detector(curr['board_type'])
                # result = True
                # sleep(2)
                test_container.process_test_result('length_detection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # short emulator
                self.signals.debug_update.emit((i, "Running: Cable emulator (short)"))
                result = ld_board.test_short_detector(curr['board_type'])
                # result = True
                # sleep(2)
                test_container.process_test_result('short_detection', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # RS485 modbus
                self.signals.debug_update.emit((i, "Running: RS485 ModBus"))
                result = ld_board.test_modbus(curr['board_type'])
                # result = True
                # sleep(2)
                test_container.process_test_result('rs485_modbus', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # RS485 ModBus
                self.signals.debug_update.emit((i, "Running: Datetime read"))
                result = ld_board.test_datetime_read()
                # result = True
                # sleep(2)
                test_container.process_test_result('datetime_read', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # write ip address
                self.signals.debug_update.emit((i, "Assigned " + LDBoardTester.ip_addresses[i]))
                result = ld_board.configure_ip_address(LDBoardTester.ip_addresses[i])
                # result = True
                # sleep(2)
                curr['tests_finished'] += 1
                curr['ethernet_participate'] = result
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Waiting for others"))

                # LED test
                self.signals.debug_update.emit((i, "Running: LED test"))
                result = ld_board.test_led(curr['board_type'])
                test_container.process_test_result('led_test', result)
                curr['tests_finished'] += 1
                curr['passing'] = curr['passing'] and result
                self.signals.update.emit((i, "Done"))

                # 4-20 mA test
                if curr['board_type'] == LDBoardTester.LD5200:
                    self.signals.debug_update.emit((i, "Running: Current source"))
                    result = ld_board.output_current()
                    # result = True
                    # sleep(2)
                    test_container.process_test_result('output_current', result)
                    curr['tests_finished'] += 1
                    curr['passing'] = curr['passing'] and result
                    self.signals.update.emit((i, "Done"))

            except ConnectionRefusalException:
                _LOGGER.error("RS232 connection refused.")
                self.process_test_result('rs232_connection', False)
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "Connection issue"))
            except ConnectionException as e:
                if e.string:
                    _LOGGER.error(e.string)
                _LOGGER.error('USB to RS485(ModBus) adapter failed to connect.')
                self.signals.alert.emit(("USB/RS485 Connection Refused", "Check that no other processes are using it."))
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "Connection issue"))
            except SerialException as e:
                if e.strerror:
                    _LOGGER.error(e.strerror)
                _LOGGER.error('USB to RS232 adapter failed to connect.')
                self.signals.alert.emit(("USB/RS232 Connection Refused", "Check that no other processes are using it."))
                curr['active'] = False
                curr['passing'] = False
                self.signals.update.emit((i, "Connection issue"))
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

            # setup logging
            # writes to logging directory with identifier
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            path = curr['log_path']
            logging.basicConfig(filename=path, filemode='a', level=logging.INFO,
                                format='{} - %(levelname)s - %(message)s'
                                .format(curr['identifier']))

            ld_board = LDBoardTester(gpio)

            # ethernet test
            self.signals.debug_update.emit((i, "Running: Ethernet test"))
            result = ld_board.test_ethernet(LDBoardTester.ip_addresses[i])
            test_container.process_test_result('ethernet_test', result)
            curr['tests_finished'] += 1
            curr['passing'] = curr['passing'] and result
            self.signals.update.emit((i, "Done"))

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


