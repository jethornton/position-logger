#!/usr/bin/python

import os, sys
import linuxcnc
from PyQt4 import uic
from PyQt4.QtGui import *


class MyWindow(QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__()
		self.s = linuxcnc.stat() # create a connection to the status channel
		try: # make sure linuxcnc is running
			self.s.poll()
		except linuxcnc.error:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setWindowTitle('Error')
			msg.setText('LinuxCNC is not running')
			msg.setInformativeText('Start LinuxCNC first.')
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
			exit()
		projectPath = os.path.abspath(os.path.dirname(sys.argv[0]))
		uic.loadUi(os.path.join(projectPath, 'position_logger.ui'), self)
		self.show()
		self.positionCB.addItem('Reletive', 'positionReletive')
		self.positionCB.addItem('Machine', 'positionMachine')
		self.setupConnections()

	def setupConnections(self):
		self.actionExit.triggered.connect(self.exit)

	def exit(self):
		exit()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())
