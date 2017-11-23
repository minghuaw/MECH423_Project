#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import *

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
		self.btnCapture.clicked.connect(self.btnCapture_clicked)

		# setup timer
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.timer_timeout)
		self.timer.start(1000)

		# setup serial flag
		self.ser_flag = False

		# setup data packet
		self.startByte = 0xff.to_bytes(1, byteorder="little", signed=False)
		self.endByte = 0x00.to_bytes(1, byteorder="little", signed=False)

		# test serial communication
		# self.read_serial_thread()

		# setup serial port
		self.ser_port = '/dev/ttyACM0'

		# set initial position
		self.x0 = 0
		self.y0 = 50 

		# set up plot
		self.grpPlot.setXRange(-xlim,xlim)
		self.grpPlot.setYRange(0,ylim)
		self.grpPlot.setMouseEnabled(False, False)
		degLeft,degRight,servoLeft,servoRight = inv_kinematics(self.x0,self.y0)
		self.send_command(servoLeft,servoRight)
		self.update_plot(degLeft,degRight,self.x0,self.y0)
		self.grpPlot.scene().sigMouseClicked.connect(self.grpPlot_clicked)
		
		# setup control timer for sending bytes and update graph
		self.cmdTimer = QTimer(self)
		self.cmdTimer.timeout.connect(self.move_trajectory)
		
		# setup video streaming timer
		self.frmTimer = QTimer(self)
		self.frmTimer.timeout.connect(self.update_frame)
		self.cap = cv2.VideoCapture(0)
		self.frmTimer.start(1000/30)
		self.captured = False

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
		self.generate_trajectory(x,y)
		
	def btnConnect_clicked(self):
		if not self.ser_flag:
			try:
				self.ser = serial.Serial(self.ser_port,9600,timeout = 1)
				print ("connection established")
				self.ser_flag = True
				self.btnConnect.setText('Disconnect')
				self.x0 = 0  # servo will return to this position after reconnect
				self.y0 = 78 # servo will return to this position after reconnect
			except serial.serialutil.SerialException:
				print ("serial port not available")
		else:
			#try:
			self.ser.close()
			print("disconnected")
			self.ser_flag = False
			self.btnConnect.setText('Connect')

	def grpPlot_clicked(self,evt):
		print ("clicked")
		mousePoint = evt.scenePos()
		# print(mousePoint)
		x = (mousePoint.x()-40)/(600-40)*2*xlim-xlim	# 40 px margin
		y = ylim-mousePoint.y()/(300-20)*ylim	# 20 px margin
		print (x,y)
		# update GUI
		self.txtPosX.setText("{:10d}".format(int(x)))
		self.txtPosY.setText("{:10d}".format(int(y)))
		# btnStart_clicked
		self.btnStart_clicked()

	def timer_timeout(self):
		portInfo = serial.tools.list_ports.comports()
		# for i in range (0,len(portInfo)):
		# 	print (portInfo[i].name)
		self.cmbPorts.clear()
		# self.cmbPorts.addItems(["1","2,","3,","4"])
		self.cmbPorts.addItems([portInfo[i].name for i in range(size(portInfo))])
		self.ser_port = '/dev/' + str(self.cmbPorts.currentText())

	def generate_trajectory(self,x,y):
		increment = 1 
		dx = x- self.x0
		dy = y- self.y0
		c = sqrt(dx**2+dy**2)
		self.steps = int(c/increment)
		self.ind = 0
		self.dx = dx/self.steps
		self.dy = dy/self.steps
		self.cmdTimer.start(10)

	def move_trajectory(self):
		# target positions
		tx = self.x0+self.dx
		ty = self.y0+self.dy
		degLeft,degRight,servoLeft,servoRight = inv_kinematics(tx,ty)
		print (servoLeft, servoRight)

		# check if solution is valid
		if math.isnan(servoLeft) or math.isnan(servoRight):
			print("Position cannot be reached")
			self.cmdTimer.stop()	
		else:
			# update current values
			self.x0 = tx
			self.y0 = ty
			print (self.x0,self.y0)
			
			# send command to arduino			
			self.send_command(servoLeft,servoRight)	

			# update GUI
			self.txtServoLeft.setText("{:10.2f}".format(degLeft))
			self.txtServoRight.setText("{:10.2f}".format(degRight))
			# update plot
			self.update_plot(degLeft,degRight,tx,ty)	
		# increase current index
		self.ind += 1
		if self.ind == self.steps:
			self.cmdTimer.stop()
	
	def send_command(self,servoLeft,servoRight):
		# convert double to int
		servoLeft = int(servoLeft)
		servoRight = int(servoRight)
			
		# Create four bytes from the integer 
		servoLeft_bytes = servoLeft.to_bytes(2, byteorder='big', signed=False)
		servoRight_bytes = servoRight.to_bytes(2, byteorder='big', signed=False)
		self.set_end_byte(servoLeft_bytes, servoRight_bytes)
		print(self.startByte, servoLeft_bytes, servoRight_bytes, self.endByte)
		
		# send command to arduino
		if self.ser_flag:
			self.ser.write(self.startByte)
			self.ser.write(servoLeft_bytes)
			self.ser.write(servoRight_bytes)
			self.ser.write(self.endByte)
		else: 
			print("Arduino cannot be found")

	def set_end_byte(self, leftBytes, rightBytes):
		high, low = bytes(leftBytes)
		if low == 255:
			self.endByte = self.endByte|0x01
		if high == 255:
			self.endByte = self.endByte|0x02

		high, low = bytes(rightBytes)
		if low == 255:
			self.endByte = self.endByte|0x10
		if high == 255:
			self.endByte = self.endByte|0x20
			
	def update_plot(self,degLeft,degRight,tx,ty):
		JLX,JLY,JRX,JRY = for_kinematics(degLeft,degRight)
		x = [O1X,JLX,tx,JRX,O2X]
		y = [O1Y,JLY,ty,JRY,O2Y]
		self.grpPlot.clear()
		self.grpPlot.plot(x,y)
		boundX = [-50,-50,50,50,-50]
		boundY = [20,80,80,20,20]
		self.grpPlot.plot(boundX,boundY)

	def plot_mouseclick(self):
		print ("mouse clicked")

	def update_frame(self):
		ret, self.frame = self.cap.read()
		self.show_image(self.frame)

	def show_image(self,img):
		# convert opencv matrix to Qimage
		img = cv2.flip(img,1)
		img = QImage(img,img.shape[1],self.frame.shape[0],self.frame.strides[0], QImage.Format_RGB888)
		self.video.setPixmap(QPixmap.fromImage(img))

	def btnCapture_clicked(self):
		if not self.captured:
			# stop video capture
			self.frmTimer.stop()
			self.cap.release()
			kernel = ones((5,5),float32)/25
			filtered = cv2.filter2D(self.frame,-1,kernel)
			gray = cv2.cvtColor(filtered,cv2.COLOR_BGR2GRAY)
			# create empty image
			height, width = gray.shape
			image = zeros((height,width,3),uint8)
			#Create default parametrization LSD
			lsd = cv2.createLineSegmentDetector(0)
			lines = lsd.detect(gray)[0]
			# iterate through lines
			for line in lines:
				pts = line[0]
				pt1 = (int(pts[0]),int(pts[1]))
				pt2 = (int(pts[2]),int(pts[3]))
				dist = sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)
				if (dist < 20):
					continue
				cv2.line(image,pt1,pt2,(0,0,255))
			self.show_image(image)
			# flip flag
			self.captured = True
			self.btnCapture.setText("Reset")
		else:
			self.cap = cv2.VideoCapture(0)
			self.frmTimer.start()
			self.captured = False
			self.btnCapture.setText("Capture")
			

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()

	sys.exit(app.exec_())

