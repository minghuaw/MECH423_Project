#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import serial
import struct


class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		# initialize setting window
		uic.loadUi('MainWindow.ui', self)
		self.move(100,100)
		self.show()
		
		# connect button signal
		self.btnConnect.clicked.connect(self.btnConnect_clicked)
		self.btnStart.clicked.connect(self.btnStart_clicked)

		# setup timer
		self.timer = QTimer(self)
		# self.timer.timeout.connect(self.timer_timeout)
		self.timer.start(1000)

	def btnStart_clicked(self):
		print ("start clicked")
		sevoLeft = 1806
		servoRight = 1053
		# Create four bytes from the integer
		servoLeft_bytes = sevoLeft.to_bytes(2, byteorder='big', signed=False)
		servoRight_bytes = servoRight.to_bytes(2, byteorder='big', signed=False)
		print(servoLeft_bytes, servoRight_bytes)
		# self.ser.write(
		

	
	def btnConnect_clicked(self):
		try:
			self.ser = serial.Serial('COM14',9600,timeout = 1)
			print ("connection established")
		except serial.serialutil.SerialException:
			print ("serial port not available")
		# print(ser.name)
		# ser.write(self.txtServoLeft,self.txtServoRight)
		# ser.close()
		
	#def timer_timeout(self):
		# self.ser.write(1234)
		# print self.ser.read()
		# portInfo = serial.tools.list_ports.comports()
		# for i in range (0,len(portInfo)):
			# print portInfo[i].name

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()

	sys.exit(app.exec_())

