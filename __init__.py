import os
import sys
import cv2
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import serial
import struct
from numpy import *
import math
import serial.tools.list_ports
import time
import threading

r1 = 40 #mm
r2 = 60 #mm
r3 = 18.5 #mm
O1X = -r3
O1Y = 0
O2X = r3
O2Y = 0
xlim = 85 # plot axis lim
ylim = 85
deg1Off = 70 
deg2Off = -deg1Off
boundXLeft = -40 # plot bound
boundXRight = 40
boundYUp = 80
boundYDown = 20

def inv_kinematics (x,y):
	# left motor
	PA1 = sqrt((x+r3)**2+y**2)
	PA2 = sqrt((x-r3)**2+y**2)
	theta11 = arccos((PA1**2+r1**2- r2**2) / (2 * r1 * PA1))
	theta12 = arccos((x+r3)/PA1)
	theta1 = theta11 + theta12
	deg1 = rad2deg(theta1)
	if(deg1 > 90+deg1Off and deg1<180+deg1Off):
		output1 = (rad2deg(theta1-pi/2)-deg1Off)/90*900+1600
	elif(deg1Off<=deg1<=90+deg1Off):
		output1 = (rad2deg(theta1)-deg1Off)/90*900+700
	else:
		output1 = nan	# set software limit
	# right motor
	theta21 = arccos((PA2**2 + r1**2 - r2**2) / (2 * r1 * PA2))
	theta22 = arccos((x-r3)/PA2)
	theta2 = -theta21 + theta22
	deg2 = rad2deg(theta2)
	if (deg2 > 90+deg2Off and deg2<180+deg2Off):
		output2 = (rad2deg(theta2-pi/2)-deg2Off)/90*1200+1500
	elif (deg2Off <= deg2 <= 90+deg2Off):
		output2 = (rad2deg(theta2)-deg2Off)/90*900+600
	else:
		output2 = nan	# set software limit 
	return deg1,deg2,output1,output2

def for_kinematics(deg1,deg2):
	# left motor
	J1X = O1X+r1*cos(deg2rad(deg1))
	J1Y = O1Y+r1*sin(deg2rad(deg1))
	J2X = O2X+r1*cos(deg2rad(deg2))
	J2Y = O2Y+r1*sin(deg2rad(deg2))
	return J1X,J1Y,J2X,J2Y
