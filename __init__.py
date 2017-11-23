import os
import sys
import cv2
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import serial
import struct
from numpy import *
import math
import serial.tools.list_ports
import time
import threading

r1 = 35 #mm
r2 = 45 #mm
# r2 = 55
r3 = 13.5 #mm
O1X = -r3
O1Y = 0
O2X = r3
O2Y = 0
def inv_kinematics (x,y):
	# left motor
	PA1 = sqrt((x+r3)**2+y**2)
	PA2 = sqrt((x-r3)**2+y**2)
	theta11 = arccos((PA1**2+r1**2- r2**2) / (2 * r1 * PA1))
	theta12 = arccos((x+r3)/PA1)
	theta1 = theta11 + theta12
	deg1 = rad2deg(theta1)
	if (deg1 >= 210):
		output1 = nan	# set software limit of 180 degrees
	elif(deg1 > 90):
		output1 = rad2deg(theta1-pi/2)/90*900+1600
	else:
		output1 = rad2deg(theta1)/90*900+700
	# right motor
	theta21 = arccos((PA2**2 + r1**2 - r2**2) / (2 * r1 * PA2))
	theta22 = arccos((x-r3)/PA2)
	theta2 = -theta21 + theta22
	deg2 = rad2deg(theta2)
	if (deg2 > 90):
		output2 = rad2deg(theta2-pi/2)/90*1200+1500
	elif (deg2 > -30):
		output2 = rad2deg(theta2)/90*900+600
	else:
		output2 = nan	# set software limit of 0 degrees
	return deg1,deg2,output1,output2

def for_kinematics(deg1,deg2):
	# left motor
	J1X = O1X+r1*cos(deg2rad(deg1))
	J1Y = O1Y+r1*sin(deg2rad(deg1))
	J2X = O2X+r1*cos(deg2rad(deg2))
	J2Y = O2Y+r1*sin(deg2rad(deg2))
	return J1X,J1Y,J2X,J2Y
