import sys
from PyQt5.QtWidgets import QMainWindow, QApplication

import view.MainWindow as app


class TheApp(QMainWindow, app.Ui_MainWindow):
    def __init__(self, parent=None):
        super(TheApp, self).__init__(parent)
        self.setupUi(self)


def main():
    app = QApplication(sys.argv)
    window = TheApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
