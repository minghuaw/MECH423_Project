#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import *
from PathWorker import PathWorker

class MainWindow(QMainWindow):
	# finish_moving = pyqtSignal()
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
		self.btnLoad.clicked.connect(self.btnLoad_clicked)

		# setup timer
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.timer_timeout)
		self.timer.start(1000)

		# set initial position
		self.x0 = 0
		self.y0 = 50

		# setup plot
		self.grpPlot.setXRange(-xlim,xlim)
		self.grpPlot.setYRange(0,ylim)
		self.grpPlot.setMouseEnabled(False, False)
		self.grpPlot.scene().sigMouseClicked.connect(self.grpPlot_clicked)
		boundX = [boundXLeft,boundXLeft,boundXRight,boundXRight,boundXLeft]
		boundY = [boundYDown,boundYUp,boundYUp,boundYDown,boundYDown]
		self.c1 = self.grpPlot.plot(boundX,boundY)
		# set servo to inital position
		degLeft,degRight,servoLeft,servoRight = inv_kinematics(self.x0,self.y0)
		JLX,JLY,JRX,JRY = for_kinematics(degLeft,degRight)
		x = [O1X,JLX,self.x0,JRX,O2X]
		y = [O1Y,JLY,self.y0,JRY,O2Y]
		self.c2 = self.grpPlot.plot(x,y)

		# setup video streaming timer
		self.frmTimer = QTimer(self)
		self.frmTimer.timeout.connect(self.update_frame)
		self.captured = "Camera" 

		# setup path worker thread
		self.thread = QThread()
		self.path_worker = PathWorker(0,50)
		# setup sig for update angle
		self.path_worker.text_sig.connect(self.update_angle)
		# setup sign for update plot
		self.path_worker.plot_sig.connect(self.update_plot)
		## move woker to thread
		self.path_worker.moveToThread(self.thread)
		self.thread.start()

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
		# self.generate_path(x,y)
		self.path_worker.generate_sig.emit(x,y)

	def btnConnect_clicked(self):
		self.path_worker.serial_sig.emit()
		if not self.path_worker.ser_flag:
			self.btnConnect.setText('Connect')
		else:
			self.btnConnect.setText('Disconnect')

	def btnLoad_clicked(self):
		fileName = QFileDialog.getOpenFileName(self,"Open Image","/home", "Image Files (*.png *.jpg *.bmp)");
		image = cv2.imread(str(fileName[0]))
		width,height = image.shape[:2]
		image = cv2.resize(image,(int(height/width*240),240),interpolation=cv2.INTER_CUBIC)
		self.show_image(image)
		self.process_image(image)

	def grpPlot_clicked(self,evt):
		# print ("clicked")
		mousePoint = evt.scenePos()
		# print(mousePoint)
		x = (mousePoint.x()-40)/(600-40)*2*xlim-xlim	# 40 px margin
		y = ylim-mousePoint.y()/(300-20)*ylim	# 20 px margin
		# print (x,y)
		# update GUI
		self.txtPosX.setText("{:10d}".format(int(x)))
		self.txtPosY.setText("{:10d}".format(int(y)))
		# generate path 
		self.path_worker.generate_sig.emit(x,y)

	def timer_timeout(self):
		portInfo = serial.tools.list_ports.comports()
		self.cmbPorts.clear()
		self.cmbPorts.addItems([portInfo[i].name for i in range(size(portInfo))])
		self.ser_port = '/dev/' + str(self.cmbPorts.currentText())

	# def generate_path(self,x,y):
	#	increment = 1 
	#	dx = x- self.x0
	#	dy = y- self.y0
	#	c = sqrt(dx**2+dy**2)
	#	self.steps = int(c/increment)
	#	self.step_ind = 0
	#	self.dx = dx/self.steps
	#	self.dy = dy/self.steps
	#	self.cmdTimer.start(10)

	# def move_path(self):
	#	# target positions
	#	tx = self.x0+self.dx
	#	ty = self.y0+self.dy
	#	degLeft,degRight,servoLeft,servoRight = inv_kinematics(tx,ty)
	#	# print (servoLeft, servoRight)

	#	# check if solution is valid
	#	if math.isnan(servoLeft) or math.isnan(servoRight):
	#		print("Position cannot be reached")
	#		self.cmdTimer.stop()	
	#	else:
	#		# update current values
	#		self.x0 = tx
	#		self.y0 = ty
	#		print (self.x0,self.y0)
	#		
	#		# send command to arduino			
	#		self.send_command(servoLeft,servoRight)	

	#		# update GUI
	#		self.txtServoLeft.setText("{:10.2f}".format(degLeft))
	#		self.txtServoRight.setText("{:10.2f}".format(degRight))
	#		# update plot
	#		self.update_plot(degLeft,degRight,tx,ty)	
	#	# increase current index
	#	self.step_ind += 1
	#	if self.step_ind == self.steps:
	#		self.cmdTimer.stop()
	#		if not math.isnan(self.point_ind):
	#			self.finish_moving.emit()
	# 
	# def send_command(self,servoLeft,servoRight):
	#	# convert double to int
	#	servoLeft = int(servoLeft)
	#	servoRight = int(servoRight)
	#		
	#	# Create four bytes from the integer 
	#	servoLeft_bytes = servoLeft.to_bytes(2, byteorder='big', signed=False)
	#	servoRight_bytes = servoRight.to_bytes(2, byteorder='big', signed=False)
	#	self.set_end_byte(servoLeft_bytes, servoRight_bytes)
	#	# print(self.startByte, servoLeft_bytes, servoRight_bytes, self.endByte)
	#	
	#	# send command to arduino
	#	if self.ser_flag:
	#		self.ser.write(self.startByte)
	#		self.ser.write(servoLeft_bytes)
	#		self.ser.write(servoRight_bytes)
	#		self.ser.write(self.endByte)
	#	else: 
	#		print("Arduino cannot be found")

	# def set_end_byte(self, leftBytes, rightBytes):
	#	high, low = bytes(leftBytes)
	#	if low == 255:
	#		self.endByte = self.endByte|0x01
	#	if high == 255:
	#		self.endByte = self.endByte|0x02

	#	high, low = bytes(rightBytes)
	#	if low == 255:
	#		self.endByte = self.endByte|0x10
	#	if high == 255:
	#		self.endByte = self.endByte|0x20
			
	def update_plot(self,degLeft,degRight,tx,ty):
		JLX,JLY,JRX,JRY = for_kinematics(degLeft,degRight)
		x = [O1X,JLX,tx,JRX,O2X]
		y = [O1Y,JLY,ty,JRY,O2Y]
		self.c2.clear()
		self.c2 = self.grpPlot.plot(x,y)

	def update_angle(self,left,right):
		self.txtServoLeft.setText(left)
		self.txtServoRight.setText(right)

	def update_frame(self):
		ret, self.frame = self.cap.read()
		self.frame = cv2.resize(self.frame,(320,240),interpolation=cv2.INTER_CUBIC)
		self.show_image(self.frame)

	def show_image(self,img):
		# convert opencv matrix to Qimage
		img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
		img = QImage(img,img.shape[1],img.shape[0],img.strides[0], QImage.Format_RGB888)
		self.video.setPixmap(QPixmap.fromImage(img))

	def btnCapture_clicked(self):
		if self.captured == "Camera":
			self.cap = cv2.VideoCapture(0)
			self.frmTimer.start(1000/30)
			self.captured = "Capture"
			self.btnCapture.setText(self.captured)
		elif self.captured == "Capture":
			# stop video capture
			self.frmTimer.stop()
			self.cap.release()
			self.process_image(self.frame)
			self.show_image(self.frame)
			# flip flag
			self.captured = "Reset" 
			self.btnCapture.setText(self.captured)
		else:
			self.captured = "Camera"
			self.btnCapture.setText(self.captured)
			self.video.clear()
			self.c3.clear()	

	def process_image(self,image):
		kernel = ones((5,5),float32)/25
		filtered = cv2.filter2D(image,-1,kernel)
		gray = cv2.cvtColor(filtered,cv2.COLOR_BGR2GRAY)
		# create empty image
		height, width = gray.shape
		image = zeros((height,width,3),uint8)
		#Create default parametrization LSD
		lsd = cv2.createLineSegmentDetector(0)
		lines = lsd.detect(gray)[0]
		sp = [] # starting points
		tp = [] # target points
		# iterate through lines
		for line in lines:
			pts = line[0]
			pt1 = (int(pts[0]),int(pts[1]))
			pt2 = (int(pts[2]),int(pts[3]))
			dist = sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)
			if (dist < 20):
				continue

			pt1_mm = [pt1[0]/320*(boundXRight-boundXLeft)+boundXLeft,-pt1[1]/240*(boundYUp-boundYDown)+boundYUp]
			pt2_mm = [pt2[0]/320*(boundXRight-boundXLeft)+boundXLeft,-pt2[1]/240*(boundYUp-boundYDown)+boundYUp]
			# if (pt1_mm[0]<-37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
			#	pt1_mm[0] = -37
			# if (pt1_mm[0]>37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
			#	pt1_mm[0] = 37
			# if (pt2_mm[0]<-37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
			#	pt2_mm[0] = -37
			# if (pt2_mm[0]>37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
			#	pt2_mm[0] = 37
			sp.append(pt1_mm)
			tp.append(pt2_mm)
			self.c3 = self.grpPlot.plot(([pt1_mm[0],pt2_mm[0]]),([pt1_mm[1],pt2_mm[1]]))
			## show processed image
			#cv2.line(image,pt1,pt2,(0,0,255))

		# sketch the lines
		self.path_worker.sketch_sig.emit(sp,tp)

	# def sketch_next_point(self):
	#	if self.lift == True:	# generate traj for start point, lift arms
	#		pt = self.start[self.point_ind]
	#		print ("lift")
	#	elif self.lift == False:	# generate traj for target point, lower arms
	#		pt = self.target[self.point_ind]
	#		print ("down")
	#	self.generate_path(pt[0],pt[1])
	#	# increase index to next point
	#	self.point_ind += 1
	#	if self.point_ind >= len(self.start):
	#		self.point_ind = nan
	#		print ("lift")

if __name__ == '__main__':
	app = QApplication(sys.argv)

	window = MainWindow()

	sys.exit(app.exec_())

