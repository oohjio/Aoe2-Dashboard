# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acknowledgements_windowrbDkxj.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AcknowledgementsWindow(object):
    def setupUi(self, AcknowledgementsWindow):
        if not AcknowledgementsWindow.objectName():
            AcknowledgementsWindow.setObjectName(u"AcknowledgementsWindow")
        AcknowledgementsWindow.resize(560, 400)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AcknowledgementsWindow.sizePolicy().hasHeightForWidth())
        AcknowledgementsWindow.setSizePolicy(sizePolicy)
        self.label = QLabel(AcknowledgementsWindow)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 20, 481, 41))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.textBrowser = QTextBrowser(AcknowledgementsWindow)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(20, 70, 520, 310))

        self.retranslateUi(AcknowledgementsWindow)

        QMetaObject.connectSlotsByName(AcknowledgementsWindow)
    # setupUi

    def retranslateUi(self, AcknowledgementsWindow):
        AcknowledgementsWindow.setWindowTitle(QCoreApplication.translate("AcknowledgementsWindow", u"Acknowledgements", None))
        self.label.setText(QCoreApplication.translate("AcknowledgementsWindow", u"Open Source  Acknowledgements", None))
        self.textBrowser.setHtml(QCoreApplication.translate("AcknowledgementsWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Noto Sans'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This software was designed by:<br /><span style=\" font-weight:600;\">oohjio</span>, <a href=\"https://github.com/oohjio\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/oohjio</span></a></p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The software is provided under a GPLv3 license. See LICENCE in project files. <br />Feel free to use it as you see fit.</p>\n"
"<p align=\"center\" style=\" margin-top:12px; margin"
                        "-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Thanks to the following packeges, that are used in this software:</p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\"\" align=\"center\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">PySide2 (Qt Bindings), <a href=\"https://www.qt.io/qt-for-python\"><span style=\" text-decoration: underline; color:#2980b9;\">https://www.qt.io/qt-for-python</span></a></li>\n"
"<li style=\"\" align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">PyQtGraph, <a href=\"https://www.pyqtgraph.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://www.pyqtgraph.org/</span></a></li>\n"
"<li style=\"\" align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-blo"
                        "ck-indent:0; text-indent:0px;\">NumPy, <a href=\"https://numpy.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://numpy.org/</span></a></li>\n"
"<li style=\"\" align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">requests, <a href=\"https://docs.python-requests.org/\"><span style=\" text-decoration: underline; color:#2980b9;\">https://docs.python-requests.org/</span></a></li>\n"
"<li style=\"\" align=\"center\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">qtmodern, <a href=\"https://github.com/gmarull/qtmodern\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/gmarull/qtmodern</span></a></li></ul></body></html>", None))
    # retranslateUi

