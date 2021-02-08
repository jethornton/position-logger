#!/usr/bin/python

import os, sys, math
import linuxcnc
# This needs to be done once at the beginning of your program,
# before the other PyQt modules are imported, and will ensure that
# a QVariant is never returned by any Qt API.
import sip
sip.setapi('QVariant', 2)

from PyQt4 import uic
from PyQt4.QtGui import (QApplication, QMainWindow, QCheckBox, QRadioButton,
QMessageBox)
from PyQt4.QtCore import Qt, QTimer

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

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
		self.qclip = QApplication.clipboard()
		self.axes = [(i) for i in range(9)if self.s.axis_mask & (1<<i)]
		self.setupGUI()
		self.setupConnections()
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(100)
		self.lastPosition = []
		self.show()


	def setupConnections(self):
		self.actionExit.triggered.connect(self.exit)
		self.logPB.clicked.connect(self.log)
		self.addExtraPB.clicked.connect(self.addExtra)
		if IN_AXIS:
			self.sendToAxisPB.setEnabled(True)
		self.sendToAxisPB.clicked.connect(self.sendToAxis)
		self.actionCopy.triggered.connect(self.copy)

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
		currentPosition = []
		for radio in self.moveGB.findChildren(QRadioButton):
			if radio.isChecked(): # add the move type
				gcode.append(str(radio.property('gcode')) + ' ')
				moveType = str(radio.property('gcode'))
		for axis in axes: # add each axis position
			axisLetter = str(getattr(self, 'axisCB_' + axis).property('axis'))
			position = str(getattr(self, 'positionLB_' + axis).text())
			currentPosition.append(float(position))
			gcode.append(axisLetter + position)

		if moveType in ['G2', 'G3']:
			if self.arcRadiusLE.text() == '':
				self.mbox('{} moves require an arc radius'.format(moveType))
				return
			if len(self.lastPosition) == 0:
				self.mbox('A G0 or G1 move must be done before a {} move'
				.format(moveType))
			x1 = self.lastPosition[0]
			x2 = currentPosition[0]
			y1 = self.lastPosition[1]
			y2 = currentPosition[1]
			if x1 == x2 and y1 == y2:
				self.mbox('{} move needs a different end point'.format(moveType))
				return
			xMid = (x1 + x2) / 2
			yMid = (y1 + y2) / 2
			slope = (y2 - y1) / (x2 - x1)
			distance = math.sqrt(pow((x1 - x2),2) + pow((y1 - y2),2))
			radius = float(self.arcRadiusLE.text())
			if radius < (distance / 2):
				self.mbox('Radius can not be smaller than {0:0.4f}'.format(distance/2))
				return

			#cosine
			c = 1/math.sqrt(1+((slope * -1)*(slope * -1)))
			#sine
			s = (slope * -1)/math.sqrt(1+((slope * -1)*(slope * -1)))

		if moveType == 'G2':
			i = xMid + radius * (c)
			j = yMid + radius * (s)
			gcode.append(' I{0:.{2}f} J{1:.{2}f}'.format(i, j, self.precisionSB.value()))
		elif moveType == 'G3':
			i = xMid + (-radius) * (c)
			j = yMid + (-radius) * (s)
			gcode.append(' I{0:.{2}f} J{1:.{2}f}'.format(i, j, self.precisionSB.value()))

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

	def copy(self):
		items = []
		gcode = [str(self.gcodeList.item(i).text()) for i in range(self.gcodeList.count())]
		self.qclip.setText('\n'.join(gcode))

	def mbox(self, message):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setWindowTitle('Error')
		msg.setText(message)
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()

	def sendToAxis(self):
		sys.stdout.write(self.g_code.get(0.0, END))

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
