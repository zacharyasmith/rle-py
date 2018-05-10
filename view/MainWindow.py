# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow_r2.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 415)
        MainWindow.setMinimumSize(QtCore.QSize(800, 415))
        MainWindow.setMaximumSize(QtCore.QSize(800, 415))
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.logo_btn = QtWidgets.QLabel(self.centralWidget)
        self.logo_btn.setGeometry(QtCore.QRect(0, 10, 211, 61))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.logo_btn.setFont(font)
        self.logo_btn.setObjectName("logo_btn")
        self.resume_btn = QtWidgets.QPushButton(self.centralWidget)
        self.resume_btn.setGeometry(QtCore.QRect(290, 10, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.resume_btn.setFont(font)
        self.resume_btn.setObjectName("resume_btn")
        self.pause_btn = QtWidgets.QPushButton(self.centralWidget)
        self.pause_btn.setGeometry(QtCore.QRect(460, 10, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pause_btn.setFont(font)
        self.pause_btn.setObjectName("pause_btn")
        self.cancel_btn = QtWidgets.QPushButton(self.centralWidget)
        self.cancel_btn.setGeometry(QtCore.QRect(630, 10, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.cancel_btn.setFont(font)
        self.cancel_btn.setObjectName("cancel_btn")
        self.tray1 = QtWidgets.QFrame(self.centralWidget)
        self.tray1.setGeometry(QtCore.QRect(10, 70, 381, 91))
        self.tray1.setStyleSheet("border: 1px solid black;")
        self.tray1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray1.setObjectName("tray1")
        self.tray1_label = QtWidgets.QLabel(self.tray1)
        self.tray1_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray1_label.setFont(font)
        self.tray1_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray1_label.setObjectName("tray1_label")
        self.tray1_progress = QtWidgets.QProgressBar(self.tray1)
        self.tray1_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray1_progress.setProperty("value", 80)
        self.tray1_progress.setTextVisible(False)
        self.tray1_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray1_progress.setInvertedAppearance(False)
        self.tray1_progress.setObjectName("tray1_progress")
        self.tray1_debug = QtWidgets.QLabel(self.tray1)
        self.tray1_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray1_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray1_debug.setObjectName("tray1_debug")
        self.tray1_info_btn = QtWidgets.QPushButton(self.tray1)
        self.tray1_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray1_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray1_info_btn.setObjectName("tray1_info_btn")
        self.tray1_cmd_btn = QtWidgets.QPushButton(self.tray1)
        self.tray1_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray1_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray1_cmd_btn.setObjectName("tray1_cmd_btn")
        self.tray1_board_label = QtWidgets.QLabel(self.tray1)
        self.tray1_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray1_board_label.setFont(font)
        self.tray1_board_label.setStyleSheet("border: none;")
        self.tray1_board_label.setObjectName("tray1_board_label")
        self.tray1_label.raise_()
        self.tray1_progress.raise_()
        self.tray1_debug.raise_()
        self.tray1_board_label.raise_()
        self.tray1_cmd_btn.raise_()
        self.tray1_info_btn.raise_()
        self.tray3 = QtWidgets.QFrame(self.centralWidget)
        self.tray3.setGeometry(QtCore.QRect(10, 290, 381, 91))
        self.tray3.setStyleSheet("border: 1px solid black;")
        self.tray3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray3.setObjectName("tray3")
        self.tray3_label = QtWidgets.QLabel(self.tray3)
        self.tray3_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray3_label.setFont(font)
        self.tray3_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray3_label.setObjectName("tray3_label")
        self.tray3_progress = QtWidgets.QProgressBar(self.tray3)
        self.tray3_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray3_progress.setProperty("value", 80)
        self.tray3_progress.setTextVisible(False)
        self.tray3_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray3_progress.setInvertedAppearance(False)
        self.tray3_progress.setObjectName("tray3_progress")
        self.tray3_debug = QtWidgets.QLabel(self.tray3)
        self.tray3_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray3_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray3_debug.setObjectName("tray3_debug")
        self.tray3_info_btn = QtWidgets.QPushButton(self.tray3)
        self.tray3_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray3_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray3_info_btn.setObjectName("tray3_info_btn")
        self.tray3_cmd_btn = QtWidgets.QPushButton(self.tray3)
        self.tray3_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray3_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray3_cmd_btn.setObjectName("tray3_cmd_btn")
        self.tray3_board_label = QtWidgets.QLabel(self.tray3)
        self.tray3_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray3_board_label.setFont(font)
        self.tray3_board_label.setStyleSheet("border: none;")
        self.tray3_board_label.setObjectName("tray3_board_label")
        self.tray2 = QtWidgets.QFrame(self.centralWidget)
        self.tray2.setGeometry(QtCore.QRect(10, 180, 381, 91))
        self.tray2.setStyleSheet("border: 1px solid black;")
        self.tray2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray2.setObjectName("tray2")
        self.tray2_label = QtWidgets.QLabel(self.tray2)
        self.tray2_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray2_label.setFont(font)
        self.tray2_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray2_label.setObjectName("tray2_label")
        self.tray2_progress = QtWidgets.QProgressBar(self.tray2)
        self.tray2_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray2_progress.setProperty("value", 80)
        self.tray2_progress.setTextVisible(False)
        self.tray2_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray2_progress.setInvertedAppearance(False)
        self.tray2_progress.setObjectName("tray2_progress")
        self.tray2_debug = QtWidgets.QLabel(self.tray2)
        self.tray2_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray2_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray2_debug.setObjectName("tray2_debug")
        self.tray2_info_btn = QtWidgets.QPushButton(self.tray2)
        self.tray2_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray2_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray2_info_btn.setObjectName("tray2_info_btn")
        self.tray2_cmd_btn = QtWidgets.QPushButton(self.tray2)
        self.tray2_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray2_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray2_cmd_btn.setObjectName("tray2_cmd_btn")
        self.tray2_board_label = QtWidgets.QLabel(self.tray2)
        self.tray2_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray2_board_label.setFont(font)
        self.tray2_board_label.setStyleSheet("border: none;")
        self.tray2_board_label.setObjectName("tray2_board_label")
        self.tray6 = QtWidgets.QFrame(self.centralWidget)
        self.tray6.setGeometry(QtCore.QRect(410, 290, 381, 91))
        self.tray6.setStyleSheet("border: 1px solid black;")
        self.tray6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray6.setObjectName("tray6")
        self.tray6_label = QtWidgets.QLabel(self.tray6)
        self.tray6_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray6_label.setFont(font)
        self.tray6_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray6_label.setObjectName("tray6_label")
        self.tray6_progress = QtWidgets.QProgressBar(self.tray6)
        self.tray6_progress.setEnabled(True)
        self.tray6_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray6_progress.setProperty("value", 80)
        self.tray6_progress.setTextVisible(False)
        self.tray6_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray6_progress.setInvertedAppearance(False)
        self.tray6_progress.setObjectName("tray6_progress")
        self.tray6_debug = QtWidgets.QLabel(self.tray6)
        self.tray6_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray6_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray6_debug.setObjectName("tray6_debug")
        self.tray6_info_btn = QtWidgets.QPushButton(self.tray6)
        self.tray6_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray6_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray6_info_btn.setObjectName("tray6_info_btn")
        self.tray6_cmd_btn = QtWidgets.QPushButton(self.tray6)
        self.tray6_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray6_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray6_cmd_btn.setObjectName("tray6_cmd_btn")
        self.tray6_board_label = QtWidgets.QLabel(self.tray6)
        self.tray6_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray6_board_label.setFont(font)
        self.tray6_board_label.setStyleSheet("border: none;")
        self.tray6_board_label.setObjectName("tray6_board_label")
        self.tray4 = QtWidgets.QFrame(self.centralWidget)
        self.tray4.setGeometry(QtCore.QRect(410, 70, 381, 91))
        self.tray4.setStyleSheet("border: 1px solid black;")
        self.tray4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray4.setObjectName("tray4")
        self.tray4_label = QtWidgets.QLabel(self.tray4)
        self.tray4_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray4_label.setFont(font)
        self.tray4_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray4_label.setObjectName("tray4_label")
        self.tray4_progress = QtWidgets.QProgressBar(self.tray4)
        self.tray4_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray4_progress.setProperty("value", 80)
        self.tray4_progress.setTextVisible(False)
        self.tray4_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray4_progress.setInvertedAppearance(False)
        self.tray4_progress.setObjectName("tray4_progress")
        self.tray4_debug = QtWidgets.QLabel(self.tray4)
        self.tray4_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray4_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray4_debug.setObjectName("tray4_debug")
        self.tray4_info_btn = QtWidgets.QPushButton(self.tray4)
        self.tray4_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray4_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray4_info_btn.setObjectName("tray4_info_btn")
        self.tray4_cmd_btn = QtWidgets.QPushButton(self.tray4)
        self.tray4_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray4_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray4_cmd_btn.setObjectName("tray4_cmd_btn")
        self.tray4_board_label = QtWidgets.QLabel(self.tray4)
        self.tray4_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray4_board_label.setFont(font)
        self.tray4_board_label.setStyleSheet("border: none;")
        self.tray4_board_label.setObjectName("tray4_board_label")
        self.tray5 = QtWidgets.QFrame(self.centralWidget)
        self.tray5.setGeometry(QtCore.QRect(410, 180, 381, 91))
        self.tray5.setStyleSheet("border: 1px solid black;")
        self.tray5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tray5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tray5.setObjectName("tray5")
        self.tray5_label = QtWidgets.QLabel(self.tray5)
        self.tray5_label.setGeometry(QtCore.QRect(350, 0, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.tray5_label.setFont(font)
        self.tray5_label.setStyleSheet("background-color: rgba(218, 218, 218, 200);\n"
"border: none;")
        self.tray5_label.setObjectName("tray5_label")
        self.tray5_progress = QtWidgets.QProgressBar(self.tray5)
        self.tray5_progress.setGeometry(QtCore.QRect(10, 66, 361, 16))
        self.tray5_progress.setProperty("value", 80)
        self.tray5_progress.setTextVisible(False)
        self.tray5_progress.setOrientation(QtCore.Qt.Horizontal)
        self.tray5_progress.setInvertedAppearance(False)
        self.tray5_progress.setObjectName("tray5_progress")
        self.tray5_debug = QtWidgets.QLabel(self.tray5)
        self.tray5_debug.setGeometry(QtCore.QRect(10, 40, 251, 21))
        self.tray5_debug.setStyleSheet("border: none;\n"
"background: white;\n"
"padding: 0 2px;")
        self.tray5_debug.setObjectName("tray5_debug")
        self.tray5_info_btn = QtWidgets.QPushButton(self.tray5)
        self.tray5_info_btn.setGeometry(QtCore.QRect(270, 40, 75, 23))
        self.tray5_info_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray5_info_btn.setObjectName("tray5_info_btn")
        self.tray5_cmd_btn = QtWidgets.QPushButton(self.tray5)
        self.tray5_cmd_btn.setGeometry(QtCore.QRect(270, 10, 75, 23))
        self.tray5_cmd_btn.setStyleSheet("background-color: rgb(225, 225, 225);")
        self.tray5_cmd_btn.setObjectName("tray5_cmd_btn")
        self.tray5_board_label = QtWidgets.QLabel(self.tray5)
        self.tray5_board_label.setGeometry(QtCore.QRect(10, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Antema")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.tray5_board_label.setFont(font)
        self.tray5_board_label.setStyleSheet("border: none;")
        self.tray5_board_label.setObjectName("tray5_board_label")
        MainWindow.setCentralWidget(self.centralWidget)
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName("status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RLE SeaLion Controller"))
        self.logo_btn.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">SeaLion</p></body></html>"))
        self.resume_btn.setText(_translate("MainWindow", "&Start"))
        self.pause_btn.setText(_translate("MainWindow", "&Pause"))
        self.cancel_btn.setText(_translate("MainWindow", "&Cancel"))
        self.tray1_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">1</p></body></html>"))
        self.tray1_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray1_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray1_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray1_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray1_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD2100</p></body></html>"))
        self.tray3_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">3</p></body></html>"))
        self.tray3_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray3_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray3_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray3_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray3_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD2100</p></body></html>"))
        self.tray2_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">2</p></body></html>"))
        self.tray2_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray2_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray2_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray2_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray2_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD2100</p></body></html>"))
        self.tray6_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">6</p></body></html>"))
        self.tray6_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray6_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray6_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray6_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray6_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD5200</p></body></html>"))
        self.tray4_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">4</p></body></html>"))
        self.tray4_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray4_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray4_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray4_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray4_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD5200</p></body></html>"))
        self.tray5_label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">5</p></body></html>"))
        self.tray5_debug.setText(_translate("MainWindow", "Running test: <test name>"))
        self.tray5_info_btn.setText(_translate("MainWindow", "Info"))
<<<<<<< HEAD
        self.tray5_cmd_btn.setText(_translate("MainWindow", "Install"))
=======
        self.tray5_cmd_btn.setText(_translate("MainWindow", "Cmd"))
>>>>>>> parent of d51d160... Change text.
        self.tray5_board_label.setText(_translate("MainWindow", "<html><head/><body><p>LD5200</p></body></html>"))

