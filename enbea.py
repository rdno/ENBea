#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from main_ui import Ui_main


class enbea(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_main()
	myWidget = QtGui.QWidget()
        self.ui.setupUi(myWidget)
	self.setCentralWidget(myWidget)
        self.setWindowTitle("ENBea")

        self.connect(self.ui.browseBtn,
                     QtCore.SIGNAL('clicked()'), self.openFileDialog)

    def openFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                    '~')
        print filename
        self.ui.showName.setText(filename)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = enbea()
    window.show()
    sys.exit(app.exec_())
