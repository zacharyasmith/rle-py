"""
view/SeaLionThread.py

Author:
    Zachary Smith
"""

import fnmatch
import logging
import os
from time import sleep

from PyQt5.QtCore import QRunnable, pyqtSlot
from serial.serialutil import SerialException
import subprocess

from components.IOUtilities import get_log_path
from components.Exceptions import ConnectionRefusalException
from components.GPIO import GPIO
from components.LDBoardTester import LDBoardTester
from view.SeaLionThread import WorkerSignals

_LOGGER = logging.getLogger()


class FirmwareInstaller(QRunnable):
    def __init__(self, gui_instance, tray: int):
        """
        Constructor
        """
        super(FirmwareInstaller, self).__init__()
        self.signals = WorkerSignals()
        self.gui = gui_instance
        self.tray_object = self.gui.objects[tray]
        self.tray = tray

    @pyqtSlot()
    def run(self):
        gui = self.gui
        logging_format = '%(levelname)s::%(message)s'

        # GPIO
        if not gui.debug:
            gpio = GPIO()
        else:
            gpio = None
        gpio.stage(GPIO.BOARD, self.tray)
        gpio.commit()

        # transfer for easier typing
        curr = self.gui.objects[self.tray]

        # setup logging
        # writes to logging directory with identifier
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        path = get_log_path(curr['identifier'])
        logging.basicConfig(filename=path, filemode='a', level=logging.INFO,
                            format=logging_format)
        curr['log_path'] = path

        # Info log
        _LOGGER.info('')
        _LOGGER.info('Installing firmware...')

        ld_board = LDBoardTester(gpio)
        try:
            # serial connection
            self.signals.debug_update.emit((self.tray, "Connecting..."))
            if not gui.debug:
                ld_board.connect_serial()
            else:
                sleep(2)

            _LOGGER.info('--')  # line break in log

            # write ip address
            self.signals.debug_update.emit((self.tray, "Assigned " + LDBoardTester.ip_addresses[self.tray]))
            if not gui.debug:
                if not ld_board.configure_ip_address(LDBoardTester.ip_addresses[self.tray]):
                    _LOGGER.error("IP assignment failed.")
                    self.signals.debug_update.emit((self.tray, "IP assignment failed"))
                    self.signals.finished.emit()
                    return
            else:
                sleep(2)

            # write file via TFTP
            directories = ['/home/pi/Desktop/', '/home/pi/']
            directory = None
            file = None
            for d in directories:
                for f in os.listdir(d):
                    if fnmatch.fnmatch(f, '{}*.bin'.format(curr['board_type'])):
                        directory = d
                        file = f
            if not directory or not file:
                _LOGGER.error("Firmware binary file not found")
                self.signals.debug_update.emit((self.tray, "File not found!"))
            else:
                self.signals.debug_update.emit((self.tray, "Uploading {}...".format(directory + file)))
                self.signals.alert.emit(("Open terminal.",
                                         "Change to `{}`, run `tftp {}`, `binary`, `put {}`"
                                         .format(directory,
                                                 LDBoardTester.ip_addresses[self.tray], file)))
                subprocess.run(['lxterminal'])

        except ConnectionRefusalException:
            _LOGGER.error("RS232 connection refused.")
            self.signals.debug_update.emit((self.tray, "RS232 connection issue"))
            self.signals.finished.emit()
            return
        except SerialException:
            _LOGGER.error('USB to RS232 adapter failed to connect.')
            self.signals.alert.emit(("USB/RS232 Connection Refused",
                                     "Check that no other processes are using it."))
            self.signals.debug_update.emit((self.tray, "RS232 connection issue"))
            self.signals.finished.emit()
            return

        # Finish up
        self.signals.debug_update.emit((self.tray, "Reset IP address: 10.0.0.188"))
        if not ld_board.configure_ip_address('10.0.0.188'):
            self.signals.debug_update.emit((self.tray, "Error with IP address reset..."))
            sleep(3)
        self.signals.finished.emit()

