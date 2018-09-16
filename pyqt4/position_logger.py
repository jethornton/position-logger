#!/usr/bin/python

import os, sys
import linuxcnc
# This needs to be done once at the beginning of your program,
# before the other PyQt modules are imported, and will ensure that
# a QVariant is never returned by any Qt API.
import sip
sip.setapi('QVariant', 2)

from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import QTimer


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
		self.axes = [(i) for i in range(9)if self.s.axis_mask & (1<<i)]
		self.setupGUI()
		self.setupConnections()
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(100)
		self.show()


	def setupConnections(self):
		self.actionExit.triggered.connect(self.exit)


	def setupGUI(self):
		self.positionCB.addItem('Relative', 'relative')
		self.positionCB.addItem('Absolute', 'absolute')

		# check axes that are and disable axes that are not
		for i in range(9):
			getattr(self, 'axisCB_' + str(i)).setChecked(i in self.axes)

	def update(self):
		self.s.poll()
		if self.positionCB.itemData(self.positionCB.currentIndex()) == 'relative':
			# sum the offsets with a negative sign
			offsets = tuple(-sum(i) for i in zip(self.s.g5x_offset,self.s.g92_offset))
			display = tuple(sum(i) for i in zip(offsets,self.s.actual_position))
			#print offsets
			#print self.s.actual_position
			#print display
		else:
			display = self.s.actual_position
		for i in self.axes:
			getattr(self, 'positionLB_' + str(i)).setText('{0:0.{1}f}'.format(display[i], self.precisionSB.value()))

	def exit(self):
		exit()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())
