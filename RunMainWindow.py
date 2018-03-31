import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFormLayout, QLineEdit, QLabel, QInputDialog
from main import start
import view.MainWindow as app


class TheApp(QMainWindow, app.Ui_MainWindow):
    def __init__(self, parent=None):
        super(TheApp, self).__init__(parent)
        self.setupUi(self)
        self.objects = dict()
        for i in range(6):
            self.objects[i] = dict()
        # assign each object to the dictionary
        self.objects[0]['tray'] = self.tray1
        self.objects[0]['cmd_btn'] = self.tray1_cmd_btn
        self.objects[0]['progress'] = self.tray1_progress
        self.objects[0]['debug'] = self.tray1_debug
        self.objects[0]['info_btn'] = self.tray1_info_btn
        self.objects[0]['board_label'] = self.tray1_board_label
        self.objects[0]['label'] = self.tray1_label

        self.objects[1]['tray'] = self.tray2
        self.objects[1]['cmd_btn'] = self.tray2_cmd_btn
        self.objects[1]['progress'] = self.tray2_progress
        self.objects[1]['debug'] = self.tray2_debug
        self.objects[1]['info_btn'] = self.tray2_info_btn
        self.objects[1]['board_label'] = self.tray2_board_label
        self.objects[1]['label'] = self.tray2_label

        self.objects[2]['tray'] = self.tray3
        self.objects[2]['cmd_btn'] = self.tray3_cmd_btn
        self.objects[2]['progress'] = self.tray3_progress
        self.objects[2]['debug'] = self.tray3_debug
        self.objects[2]['info_btn'] = self.tray3_info_btn
        self.objects[2]['board_label'] = self.tray3_board_label
        self.objects[2]['label'] = self.tray3_label

        self.objects[3]['tray'] = self.tray4
        self.objects[3]['cmd_btn'] = self.tray4_cmd_btn
        self.objects[3]['progress'] = self.tray4_progress
        self.objects[3]['debug'] = self.tray4_debug
        self.objects[3]['info_btn'] = self.tray4_info_btn
        self.objects[3]['board_label'] = self.tray4_board_label
        self.objects[3]['label'] = self.tray4_label

        self.objects[4]['tray'] = self.tray5
        self.objects[4]['cmd_btn'] = self.tray5_cmd_btn
        self.objects[4]['progress'] = self.tray5_progress
        self.objects[4]['debug'] = self.tray5_debug
        self.objects[4]['info_btn'] = self.tray5_info_btn
        self.objects[4]['board_label'] = self.tray5_board_label
        self.objects[4]['label'] = self.tray5_label

        self.objects[5]['tray'] = self.tray6
        self.objects[5]['cmd_btn'] = self.tray6_cmd_btn
        self.objects[5]['progress'] = self.tray6_progress
        self.objects[5]['debug'] = self.tray6_debug
        self.objects[5]['info_btn'] = self.tray6_info_btn
        self.objects[5]['board_label'] = self.tray6_board_label
        self.objects[5]['label'] = self.tray6_label
        for i in range(6):
            self.objects[i]['debug'].setText("Awaiting start.")
            self.objects[i]['progress'].setValue(0)
            # self.objects[i]['cmd_btn'].clicked.connect(lambda: clicked(i + 1))
            self.objects[i]['info_btn'].setDisabled(True)
        self.set_status(-1, self.WAITING)
        self.pause_btn.setDisabled(True)
        self.cancel_btn.setDisabled(True)
        self.resume_btn.clicked.connect(self.start_btn_handler)

    # create other constants
    INACTIVE = "#f2f2f2"
    FAIL = "#FF5B5B"
    PASSING = "#33CC33"
    WAITING = "#FFA500"

    def start_btn_handler(self):
        self.resume_btn.setDisabled(True)
        proceed = True
        for i in range(6):
            board = "Tray {}".format(i + 1)
            mac, ok = QInputDialog.getText(self, 'MAC', "Enter MAC Address ({})".format(board))
            if not ok:
                proceed = False
                break
            serial, ok1 = QInputDialog.getText(self, "Serial", "Enter Serial ID ({})".format(board))
            if ok and ok1:
                if len(mac) > 0 and len(serial) > 0:
                    self.objects[i]["mac"] = mac
                    self.objects[i]["serial"] = serial
                    self.set_status(i, self.PASSING)
                else:
                    self.set_status(i, self.INACTIVE)
            else:
                proceed = False
                break
        if proceed:
            # Exec tests
            pass
        else:
            self.set_status(-1, self.WAITING)
        self.resume_btn.setDisabled(False)

    def set_status(self, tray, status):
        if tray == -1:
            for i in range(6):
                self.objects[i]['label'].setStyleSheet("background-color: {}".format(status))
        else:
            self.objects[tray]['label'].setStyleSheet("background-color: {}".format(status))


def main():
    app = QApplication(sys.argv)
    window = TheApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
