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
from PyQt4.QtCore import Qt, QTimer


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
		self.logPB.clicked.connect(self.log)
		self.addExtraPB.clicked.connect(self.addExtra)
		self.testPB.clicked.connect(self.test)


	def setupGUI(self):
		self.positionCB.addItem('Relative', 'relative')
		self.positionCB.addItem('Absolute', 'absolute')

		# check axes that are and disable axes that are not
		for i in range(9):
			getattr(self, 'axisCB_' + str(i)).setChecked(i in self.axes)

	def log(self):
		axes = []
		for checkbox in self.axesGB.findChildren(QCheckBox): # get axes list
			if checkbox.isChecked():
				axes.insert(0, str(checkbox.objectName()[-1]))

		gcode = []
		for radio in self.moveGB.findChildren(QRadioButton):
			if radio.isChecked(): # add the move type
				gcode.append(str(radio.property('gcode')) + ' ')
				moveType = str(radio.property('gcode'))
		for axis in axes: # add each axis position
			axisLetter = str(getattr(self, 'axisCB_' + axis).property('axis'))
			position = str(getattr(self, 'positionLB_' + axis).text())
			gcode.append(axisLetter + position)

		if moveType == 'G2':
			print 'G2'
			return
		elif moveType == 'G3':
			print 'G3'
			return

		if moveType in ['G1', 'G2', 'G3']: # check for a feed rate
			feedMatch = self.gcodeList.findItems('F', Qt.MatchContains)
			if len(feedMatch) > 0: # check last feed rate to see if it is different
				lastMatch =  str(feedMatch[-1].text()).split()
				if lastMatch[-1][1:] != self.feedLE.text():
					gcode.append(' F{}'.format(str(self.feedLE.text())))
			if not self.gcodeList.findItems('F', Qt.MatchContains):
				if self.feedLE.text():
					gcode.append(' F{}'.format(str(self.feedLE.text())))
				else:
					self.mbox('A feed rate must be entered for a {} move'.format(moveType))
					return

		self.gcodeList.addItem(''.join(gcode))
		self.lastPosition = []
		for axis in axes:
			self.lastPosition.append(float(getattr(self, 'positionLB_' + axis).text()))

	def addExtra(self):
		self.gcodeList.addItem(self.extraLE.text())

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

	def mbox(self, message):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setWindowTitle('Error')
		msg.setText(message)
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()

	def test(self):
		#print self.gcodeList.count()
		items = self.gcodeList.findItems('F', Qt.MatchContains)
		#print self.gcodeList.row(items[-1])
		testCode =  str(items[-1].text()).split()
		if testCode[-1][1:] != self.feedLE.text():
			print 'not'
		#if len(items) > 0:
		#	for item in items:
		#		print "row number of found item =",self.gcodeList.row(item)
		#		print "text of found item =",item.text() 

	def exit(self):
		exit()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MyWindow()
	sys.exit(app.exec_())
