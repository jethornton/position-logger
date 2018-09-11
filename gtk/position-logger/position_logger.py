#! /usr/bin/env python
# -*- coding: utf-8 -*-
version = '0.1'

import os, sys
import gtk
import time
import linuxcnc
import gobject

class app:
	def __init__(self):
		self.builder = gtk.Builder()
		self.path = os.path.abspath(os.path.dirname(sys.argv[0]))
		self.ui = os.path.join(self.path, 'position_logger.glade')
		self.builder.add_from_file(self.ui)
		self.builder.connect_signals(self)
		self.statusbar = self.builder.get_object("statusbar")
		self.context_id = self.statusbar.get_context_id("status")
		self.status_count = 0
		self.s = linuxcnc.stat() # create a connection to the status channel
		try:
			self.s.poll()
		except linuxcnc.error:
			#print"error", detail
			#print type(detail)
			self.statusbar.push(self.context_id, 'Start LinuxCNC then run this Program')
			self.emc = False
		else:
			self.statusbar.push(self.context_id, 'LinuxCNC is running')
			self.emc = True

		self.display_cb = self.builder.get_object('display_cb')
		self.display = 'Relative'
		self.display_ls = gtk.ListStore(int,str)
		self.display_ls.append([0,"Relative"])
		self.display_ls.append([1,"Absolute"])
		self.display_cb.set_model(self.display_ls)
		self.cell = gtk.CellRendererText()
		self.display_cb.pack_start(self.cell, True)
		self.display_cb.add_attribute(self.cell, 'text', 1)
		self.display_cb.set_active(0)


		self.log_0 = self.builder.get_object('log_0')
		self.log_1 = self.builder.get_object('log_1')
		self.log_2 = self.builder.get_object('log_2')
		self.log_3 = self.builder.get_object('log_3')
		self.log_4 = self.builder.get_object('log_4')
		self.log_5 = self.builder.get_object('log_5')
		self.log_6 = self.builder.get_object('log_6')
		self.log_7 = self.builder.get_object('log_7')
		self.log_8 = self.builder.get_object('log_8')
		axis_names = {0:'X', 1:'Y', 2:'Z', 3:'A', 4:'B', 5:'C', 6:'U', 7:'V', 8:'W', }
		if self.emc:
			for i in range(self.s.axes):
				eval('self.log_' + str(i) + '.set_active(True)')
				#print axis_names[i] , '{:.4f}'.format(self.s.position[i]-self.s.g5x_offset[i])
			#print self.s.position[0]

		gobject.timeout_add(100, self.update)
		self.pos_0 = self.builder.get_object('pos_0')
		self.pos_1 = self.builder.get_object('pos_1')
		self.pos_2 = self.builder.get_object('pos_2')
		self.pos_3 = self.builder.get_object('pos_3')
		self.pos_4 = self.builder.get_object('pos_4')
		self.pos_5 = self.builder.get_object('pos_5')
		self.pos_6 = self.builder.get_object('pos_6')
		self.pos_7 = self.builder.get_object('pos_7')
		self.pos_8 = self.builder.get_object('pos_8')

		self.insert_text = self.builder.get_object('insert_text')
		self.textview = self.builder.get_object('textview')
		self.textbuffer = self.textview.get_buffer()
		self.textbuffer.set_text('; Generated by Position Logger')

		self.g0_rb = self.builder.get_object('g0_rb')
		self.g1_rb = self.builder.get_object('g1_rb')

		self.window = self.builder.get_object('window')
		self.window.show_all()

	def log_clicked(self, widget):
		if self.g0_rb.get_active():
			que = 'G0 '
		else:
			que = 'G1 '
		if self.log_0.get_active():
			que += 'X' + self.pos_0.get_text() + ' '
		if self.log_1.get_active():
			que += 'Y' + self.pos_1.get_text() + ' '
		if self.log_2.get_active():
			que += 'Z' + self.pos_2.get_text() + ' '
		if self.log_3.get_active():
			que += 'A' + self.pos_3.get_text() + ' '
		if self.log_4.get_active():
			que += 'B' + self.pos_4.get_text() + ' '
		if self.log_5.get_active():
			que += 'C' + self.pos_5.get_text() + ' '
		if self.log_6.get_active():
			que += 'U' + self.pos_6.get_text() + ' '
		if self.log_7.get_active():
			que += 'V' + self.pos_7.get_text() + ' '
		if self.log_8.get_active():
			que += 'W' + self.pos_8.get_text() + ' '
		end_iter = self.textbuffer.get_end_iter()
		self.textbuffer.insert(end_iter, '\n' + que)


	def insert_btn_clicked(self, widget):
		end_iter = self.textbuffer.get_end_iter()
		self.textbuffer.insert(end_iter, '\n' + self.insert_text.get_text())

	def on_display_cb_changed(self, widget, data=None):
		# get the index of the changed row
		self.index = widget.get_active()
		# get the model
		self.model = widget.get_model()
		# retrieve the item from column 1
		self.item = self.model[self.index][1]
		self.display = self.item

	def update(self):
		self.s.poll()
		if self.display == 'Relative':
			for i in range(self.s.axes):
				eval('self.pos_' + str(i) + '.set_text("{:.4f}".format(self.s.position[' + str(i) + ']-self.s.g5x_offset[' + str(i) + ']))')
		else:
			for i in range(self.s.axes):
				eval('self.pos_' + str(i) + '.set_text("{:.4f}".format(self.s.axis[' + str(i) + ']["output"]))')
		return True

	def window_destroy(self, *args):
		# do some checks to see if unsaved and annoy
		gtk.main_quit(*args)


main = app()
gtk.main()
