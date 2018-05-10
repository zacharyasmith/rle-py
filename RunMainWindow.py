#!/usr/bin/env python3
"""
RunMainWindow.py

Author:
    Zachary Smith
"""
import sys

import argparse
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QErrorMessage, QMessageBox
from PyQt5.QtCore import QThreadPool
import re
from view.SeaLionThread import SeaLionThread, TimeUpdater
import view.MainWindow as Main
from components.LDBoardTester import LDBoardTester
from datetime import datetime
import threading


class SeaLionGUI(QMainWindow, Main.Ui_MainWindow):
    def __init__(self, parent=None, debug=False):
        super(SeaLionGUI, self).__init__(parent)
        self.setupUi(self)

        # for signalling
        self.debug = debug
        self.pause = False
        self.cancel = False
        self.test_start = None
        self.testing = False

        # setup thread pool
        self.thread_pool = QThreadPool()
        self.thread_lock = threading.Lock()     # type: threading.Lock

        self.objects = dict()
        for i in range(6):
            self.objects[i] = dict()

        # assign each object to the dictionary
        # LD2100 Tray 1 : GPIO address 3
        self.objects[0]['board_type'] = LDBoardTester.LD2100
        self.objects[0]['identifier'] = "LD2100_1"
        self.objects[0]['GPIO_address'] = 3
        self.objects[0]['tray'] = self.tray1
        self.objects[0]['cmd_btn'] = self.tray1_cmd_btn
        self.objects[0]['progress'] = self.tray1_progress
        self.objects[0]['debug'] = self.tray1_debug
        self.objects[0]['info_btn'] = self.tray1_info_btn
        self.objects[0]['board_label'] = self.tray1_board_label
        self.objects[0]['label'] = self.tray1_label
        self.tray1_info_btn.clicked.connect(self.info_btn_handler_1)

        # LD2100 Tray 2 : GPIO address 4
        self.objects[1]['board_type'] = LDBoardTester.LD2100
        self.objects[1]['identifier'] = "LD2100_2"
        self.objects[1]['GPIO_address'] = 4
        self.objects[1]['tray'] = self.tray2
        self.objects[1]['cmd_btn'] = self.tray2_cmd_btn
        self.objects[1]['progress'] = self.tray2_progress
        self.objects[1]['debug'] = self.tray2_debug
        self.objects[1]['info_btn'] = self.tray2_info_btn
        self.objects[1]['board_label'] = self.tray2_board_label
        self.objects[1]['label'] = self.tray2_label
        self.tray2_info_btn.clicked.connect(self.info_btn_handler_2)

        # LD2100 Tray 3 : GPIO address 3
        self.objects[2]['board_type'] = LDBoardTester.LD2100
        self.objects[2]['identifier'] = "LD2100_3"
        self.objects[2]['GPIO_address'] = 5
        self.objects[2]['tray'] = self.tray3
        self.objects[2]['cmd_btn'] = self.tray3_cmd_btn
        self.objects[2]['progress'] = self.tray3_progress
        self.objects[2]['debug'] = self.tray3_debug
        self.objects[2]['info_btn'] = self.tray3_info_btn
        self.objects[2]['board_label'] = self.tray3_board_label
        self.objects[2]['label'] = self.tray3_label
        self.tray3_info_btn.clicked.connect(self.info_btn_handler_3)

        # LD5200 Tray 4 : GPIO address 0
        self.objects[3]['board_type'] = LDBoardTester.LD5200
        self.objects[3]['identifier'] = "LD5200_4"
        self.objects[3]['GPIO_address'] = 0
        self.objects[3]['tray'] = self.tray4
        self.objects[3]['cmd_btn'] = self.tray4_cmd_btn
        self.objects[3]['progress'] = self.tray4_progress
        self.objects[3]['debug'] = self.tray4_debug
        self.objects[3]['info_btn'] = self.tray4_info_btn
        self.objects[3]['board_label'] = self.tray4_board_label
        self.objects[3]['label'] = self.tray4_label
        self.tray4_info_btn.clicked.connect(self.info_btn_handler_4)

        # LD5200 Tray 5 : GPIO address 1
        self.objects[4]['board_type'] = LDBoardTester.LD5200
        self.objects[4]['identifier'] = "LD5200_5"
        self.objects[4]['GPIO_address'] = 1
        self.objects[4]['tray'] = self.tray5
        self.objects[4]['cmd_btn'] = self.tray5_cmd_btn
        self.objects[4]['progress'] = self.tray5_progress
        self.objects[4]['debug'] = self.tray5_debug
        self.objects[4]['info_btn'] = self.tray5_info_btn
        self.objects[4]['board_label'] = self.tray5_board_label
        self.objects[4]['label'] = self.tray5_label
        self.tray5_info_btn.clicked.connect(self.info_btn_handler_5)

        # LD5200 Tray 6 : GPIO address 2
        self.objects[5]['board_type'] = LDBoardTester.LD5200
        self.objects[5]['identifier'] = "LD5200_6"
        self.objects[5]['GPIO_address'] = 2
        self.objects[5]['tray'] = self.tray6
        self.objects[5]['cmd_btn'] = self.tray6_cmd_btn
        self.objects[5]['progress'] = self.tray6_progress
        self.objects[5]['debug'] = self.tray6_debug
        self.objects[5]['info_btn'] = self.tray6_info_btn
        self.objects[5]['board_label'] = self.tray6_board_label
        self.objects[5]['label'] = self.tray6_label
        self.tray6_info_btn.clicked.connect(self.info_btn_handler_6)

        self.reset_trays()
        self.pause_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        self.resume_btn.clicked.connect(self.start_btn_handler)
        self.pause_btn.clicked.connect(self.pause_btn_handler)
        self.cancel_btn.clicked.connect(self.cancel_btn_handler)

    # create other constants
    INACTIVE = "#f2f2f2"
    FAIL = "#FF5B5B"
    PASSING = "#33CC33"
    WAITING = "#FFA500"

    def start_btn_handler(self) -> None:
        """
        The method called when start button is clicked.
        Will process each MAC/Serial combo and execute SeaLionThread when done.
        :return: None
        """
        if self.testing:
            self.resume_btn_handler()
            return
        self.status_bar.showMessage("Starting...")
        self.resume_btn.setDisabled(True)
        self.update_progress(-1, 0, 1)
        self.set_status(-1, self.WAITING)
        self.update_debug_text(-1, "...")
        proceed = True
        for i in range(6):
            board = "Tray {}".format(i + 1)
            mac, ok = QInputDialog.getText(self, 'MAC', "Enter MAC Address ({})".format(board))
            if not ok:
                proceed = False
                break
            elif len(mac) > 0:
                if not self.debug:
                    mac, ok = self.__prompt_mac_address(mac, board)
                if not ok:
                    proceed = False
                    break
            else:
                self.objects[i]["active"] = False
                self.set_status(i, self.INACTIVE)
                continue
            serial, ok1 = QInputDialog.getText(self, "Serial", "Enter Serial ID ({})".format(board))
            if ok and ok1:
                if len(mac) > 0 and len(serial) > 0:
                    self.objects[i]["mac"] = mac
                    self.objects[i]["serial"] = serial
                    self.objects[i]["active"] = True
                    self.set_status(i, self.PASSING)
                    self.update_debug_text(i, "Waiting to start")
                else:
                    self.objects[i]["active"] = False
                    self.set_status(i, self.INACTIVE)
            else:
                proceed = False
                break
        if proceed:
            # disable buttons
            self.set_cmd_btn_diabled(-1, True)
            self.set_info_btn_disabled(-1, True)
            # enable pause/cancel
            self.pause_btn.setDisabled(False)
            self.cancel_btn.setDisabled(False)
            # starting the worker
            worker = SeaLionThread(self)
            worker.signals.finished.connect(self._signal_test_finished)
            worker.signals.alert.connect(self._signal_alert)
            worker.signals.debug_update.connect(self._signal_debug_update)
            worker.signals.update.connect(self._signal_update)
            self.thread_pool.start(worker)
            # test started
            self.testing = True
            self.test_start = datetime.now()
            time_thread = TimeUpdater(self)
            time_thread.signals.status_bar.connect(self._signal_status_bar)
            self.thread_pool.start(time_thread)
            return
        else:
            self.reset_trays()
        self.resume_btn.setDisabled(False)

    def resume_btn_handler(self) -> None:
        self.thread_lock.acquire()
        print("Resume")
        self.pause_btn.setDisabled(False)
        self.resume_btn.setDisabled(True)
        self.pause = False
        self.thread_lock.release()

    def pause_btn_handler(self) -> None:
        self.thread_lock.acquire()
        print("Pause")
        self.pause_btn.setDisabled(True)
        self.resume_btn.setDisabled(False)
        self.cancel = False
        self.pause = True
        self.thread_lock.release()

    def cancel_btn_handler(self) -> None:
        self.thread_lock.acquire()
        print("Cancel")
        self.pause = False
        self.cancel = True
        self.thread_lock.release()

    def __prompt_mac_address(self, attempt: str, tray: str) -> tuple:
        match = re.match(r'^([0-9A-F]{2}:){5}([0-9A-F]{2})$', attempt)
        if not match:
            msg_box = QMessageBox(self)
            msg_box.setText("Type MAC address correctly. ex. 12:34:56:AB:CD:EF")
            msg_box.exec_()
            mac, ok = QInputDialog.getText(self, 'MAC', "Enter MAC Address Again ({})".format(tray))
            if not ok:
                return mac, ok
            return self.__prompt_mac_address(mac, tray)
        else:
            return attempt, True

    def set_status(self, tray: int, status: str) -> None:
        """
        Sets the status `LED` for each tray. Uses Hex RGB values.

        :param tray: int selector. -1 for all
        :param status: Hex RGB
        :return: None
        """
        if tray == -1:
            for i in range(6):
                self.objects[i]['label'].setStyleSheet("background-color: {}".format(status))
        else:
            self.objects[tray]['label'].setStyleSheet("background-color: {}".format(status))

    def test_passing(self, tray: int, passing: bool) -> None:
        """
        Sets the status `LED` to pass or fail.

        :param tray: int selector
        :param passing: bool whether the tray is passing or not
        :return: None
        """
        self.set_status(tray, self.PASSING if passing else self.FAIL)

    def update_progress(self, tray: int, count: int, total: int) -> None:
        """
        Update the progress bar.

        :param tray: int selector. -1 for all.
        :param count: int count of tests passed
        :param total: int count total tests
        :return: None
        """
        if tray == -1:
            for i in range(6):
                self.objects[i]['progress'].setMaximum(total)
                self.objects[i]['progress'].setValue(count)
        else:
            self.objects[tray]['progress'].setMaximum(total)
            self.objects[tray]['progress'].setValue(count)

    def update_debug_text(self, tray: int, text: str) -> None:
        """
        Updates the text in the tray. Useful for operator.

        :param tray: int selector. -1 for all.
        :param text: str message to be displayed
        :return: None
        """
        if tray == -1:
            for i in range(6):
                self.objects[i]['debug'].setText(text)
        else:
            self.objects[tray]['debug'].setText(text)

    def set_cmd_btn_diabled(self, tray: int, value: bool) -> None:
        """
        Disables the command button or re-enables

        :param tray: int selector. -1 for all
        :param value: bool wether it disables or re-enables
        :return: None
        """
        if tray == -1:
            for i in range(6):
                self.objects[i]['cmd_btn'].setDisabled(value)
        else:
            self.objects[tray]['cmd_btn'].setDisabled(value)

    def set_info_btn_disabled(self, tray: int, value: bool) -> None:
        """
        Disables the info button or re-enables

        :param tray: int selector. -1 for all
        :param value: bool whether it disables or re-enables
        :return: None
        """
        if tray == -1:
            for i in range(6):
                self.objects[i]['info_btn'].setDisabled(value)
        else:
            self.objects[tray]['info_btn'].setDisabled(value)

    def reset_trays(self) -> None:
        """
        Resets the trays to waiting state.

        :return: None
        """
        self.update_progress(-1, 0, 1)
        self.update_debug_text(-1, "Awaiting start.")
        self.status_bar.showMessage("")
        self.set_info_btn_disabled(-1, True)
        self.set_status(-1, self.WAITING)

    def _signal_alert(self, message: tuple) -> None:
        """
        message: (type: str, text: str)
        """
        QErrorMessage(self).showMessage('*{}* {}'.format(message[0], message[1]))

    def _signal_debug_update(self, data: tuple):
        """
        data: (tray: int, text: str)
        """
        self.update_debug_text(data[0], data[1])

    def _signal_update(self, data: tuple):
        """
        data: (tray: int, debug_text: str)
        """
        tray = self.objects[data[0]]
        self.update_debug_text(data[0], data[1])
        self.update_progress(data[0], tray['tests_finished'], tray['tests_total'])
        self.test_passing(data[0], tray['passing'])

    def _signal_status_bar(self, message: str):
        """
        message: str
        """
        self.status_bar.showMessage(message)

    def _signal_test_finished(self) -> None:
        """
        signaled from thread that all tests are completed
        """
        self.thread_lock.acquire()
        print("Finished")
        self.pause_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        self.resume_btn.setDisabled(False)
        self.set_cmd_btn_diabled(-1, False)
        self.set_info_btn_disabled(-1, True)
        self.testing = False
        self.pause = False
        self.cancel = False
        self.thread_lock.release()
        for i in range(6):
            if self.objects[i]['log_path']:
                self.set_info_btn_disabled(i, False)
        # TODO write results to file

    """
    Each of the info buttons have their own handler
    """
    def info_btn_handler_1(self) -> None:
        self.info_btn_handler(0)

    def info_btn_handler_2(self) -> None:
        self.info_btn_handler(1)

    def info_btn_handler_3(self) -> None:
        self.info_btn_handler(2)

    def info_btn_handler_4(self) -> None:
        self.info_btn_handler(3)

    def info_btn_handler_5(self) -> None:
        self.info_btn_handler(4)

    def info_btn_handler_6(self) -> None:
        self.info_btn_handler(5)

    def info_btn_handler(self, tray: int) -> None:
        # thatLine = thatLine.replace('\n', '<br />')
        path = self.objects[tray]['log_path']
        import subprocess
        subprocess.run(['leafpad', path])
        pass

    def cmd_btn_handler_1(self) -> None:
        self.cmd_btn_handler(0)

    def cmd_btn_handler_2(self) -> None:
        self.cmd_btn_handler(1)

    def cmd_btn_handler_3(self) -> None:
        self.cmd_btn_handler(2)

    def cmd_btn_handler_4(self) -> None:
        self.cmd_btn_handler(3)

    def cmd_btn_handler_5(self) -> None:
        self.cmd_btn_handler(4)

    def cmd_btn_handler_6(self) -> None:
        self.cmd_btn_handler(5)

    def cmd_btn_handler(self, tray: int) -> int:
        # self.objects[0]['board_type'] = LDBoardTester.LD2100
        # self.objects[0]['identifier'] = "LD2100_1"
        # self.objects[0]['GPIO_address'] = 3
        # self.objects[0]['cmd_btn'] = self.tray1_cmd_btn
        pass


def main(debug=False) -> None:
    app = QApplication(sys.argv)
    window = SeaLionGUI(debug=debug)
    window.show()
    app.exec_()


if __name__ == '__main__':
    # argument parser
    parser = argparse.ArgumentParser(description='RLE LD Board Tester.')
    # verbosity
    parser.add_argument('--debug', '-d', action="count",
                        help='Counts number of `v`s in flag. More flags is more verbose.')
    args = vars(parser.parse_args())
    if args['debug']:
        main(True)
    main()
