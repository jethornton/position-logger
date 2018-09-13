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
		self.setupGUI()
		self.setupConnections()
		self.show()

	def setupConnections(self):
		self.actionExit.triggered.connect(self.exit)

	def setupGUI(self):
		self.positionCB.addItem('Reletive', 'positionReletive')
		self.positionCB.addItem('Machine', 'positionMachine')

		# check axes that are and disable axes that are not
        #  axes = [(i) for i in range(9)if mask & (1<<i)]
		axisMask = self.s.axis_mask
        axes = [(i) for i in range(9)if axisMask & (1<<i)]
        for i in range(9):
            getattr(self, 'axisCB_' + str(i)).setChecked(i in axes)
        
        """
		axisList = [1, 2, 4, 8, 16, 32, 64, 128, 256]
		possibleAxes = []
		for axis in axisList:
			if axis <= self.s.axis_mask:
				possibleAxes.append(axis)
		axesList = []
		for i in range(len(possibleAxes)):
			if max(possibleAxes) <= axisMask:
				axesList.append(max(possibleAxes))
				axisMask = axisMask - max(possibleAxes)
			possibleAxes.remove(max(possibleAxes))
		for axis in axesList:
			axisList.remove(axis)
			getattr(self, 'axisCB_' + str(axis)).setChecked(True)
		for axis in axisList:
			getattr(self, 'axisCB_' + str(axis)).setEnabled(False)
        """


	def exit(self):
		exit()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())
