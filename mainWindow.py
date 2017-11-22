#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import *

import os
import sys
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import serial
import serial.tools.list_ports
import struct
import time


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
		self.timer.timeout.connect(self.timer_timeout)
		self.timer.start(1000)

		# setup serial flag
		self.ser_flag = False

		# set initial position
		self.x0 = 0
		self.y0 = 10

	def retrieve_XY(self):
		try:
			x = int(self.txtPosX.toPlainText())
			y = int(self.txtPosY.toPlainText())	
		except ValueError:
			x= nan
			y = nan
		return x,y

	def btnStart_clicked(self):
		#print ("start clicked")
		x,y = self.retrieve_XY()
		if math.isnan(x) or math.isnan(y):
			print("Please enter X,Y values")
			return 
		self.move_trajectory(x,y)
		
	def btnConnect_clicked(self):
		if not self.ser_flag:
			try:
				self.ser = serial.Serial('/dev/ttyACM0',9600,timeout = 1)
				print ("connection established")
				self.ser_flag = True
				self.btnConnect.setText('Disconnect')	
			except serial.serialutil.SerialException:
				print ("serial port not available")
		else:
			#try:
			self.ser.close()
			print("disconnected")
			ser.ser_flag = false
			serl.btnConnect.setText('Connect')
		# print(ser.name)
		# ser.write(self.txtServoLeft,self.txtServoRight)
		# ser.close()
		
	def timer_timeout(self):
		portInfo = serial.tools.list_ports.comports()
		for i in range (0,len(portInfo)):
			print (portInfo[i].name)
		self.cmbPorts.clear()
		self.cmbPorts.addItems(["1","2,","3,","4"])

	def move_trajectory(self,x,y):
		increment = 1 
		dx = x- self.x0
		dy = y- self.y0
		c = sqrt(dx**2+dy**2)
		steps = int(c/increment)
		for i in range (0,steps):
			# target positions
			tx = self.x0+dx/steps
			ty = self.y0+dy/steps
			degLeft, degRight,servoLeft,servoRight = inv_kinematics(tx,ty)
			print (servoLeft, servoRight)

			# check if solution is valid
			if math.isnan(servoLeft) or math.isnan(servoRight):
				print("Position cannot be reached")
				break
			else:
				# update current values
				self.x0 = tx
				self.y0 = ty
				print (self.x0,self.y0)
				# convert double to int
				servoLeft = int(servoLeft)
				servoRight = int(servoRight)
			
				# Create four bytes from the integer
				servoLeft_bytes = servoLeft.to_bytes(2, byteorder='big', signed=False)
				servoRight_bytes = servoRight.to_bytes(2, byteorder='big', signed=False)
				print(servoLeft_bytes, servoRight_bytes)
		
				if self.ser_flag:
					self.ser.write(servoLeft_bytes)
					self.ser.write(servoRight_bytes)
				else:
					print("Arduino cannot be found")
				# update GUI not working.... probably need multithreading
				self.txtServoLeft.setText("{:10.2f}".format(degLeft))
				self.txtServoRight.setText("{:10.4f}".format(degRight))
			# delay for 50ms	
			time.sleep(0.05)

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()

	sys.exit(app.exec_())

