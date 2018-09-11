#!/usr/bin/python
import os, sys
from PyQt4 import QtGui, uic

class MyWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__()
		projectPath = os.path.abspath(os.path.dirname(sys.argv[0]))
		uic.loadUi(os.path.join(projectPath, 'position_logger.ui'), self)
		self.show()
		self.positionCB.addItem('Reletive', 'positionReletive')
		self.positionCB.addItem('Machine', 'positionMachine')
		self.setupConnections()

	def setupConnections(self):
		self.actionExit.triggered.connect(self.exit())

	def exit(self):
		print 'exit'
		exit()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())
