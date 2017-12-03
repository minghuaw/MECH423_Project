#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __init__ import *
from PathWorker import PathWorker
from ContourImage import ContourImage

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
			
		# setup contour detector
		self.contourImage = ContourImage()

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
		self.frame = self.contourImage.returnFrame()
		roi = self.frame[:480,(320-180):(320+180)]
		self.frame = cv2.resize(roi,(480,640),interpolation=cv2.INTER_CUBIC)
		# flip to get mirrored effect
		flipped = cv2.flip(self.frame,flipCode=1)
		self.show_image(flipped)

	def show_image(self,img):
		# convert opencv matrix to Qimage
		img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
		img = QImage(img,img.shape[1],img.shape[0],img.strides[0], QImage.Format_RGB888)
		self.video.setPixmap(QPixmap.fromImage(img))

	def btnCapture_clicked(self):
		if self.captured == "Camera":
			self.contourImage.openCam()
			#self.cap = cv2.VideoCapture(0)
			self.frmTimer.start(1000/30)
			self.captured = "Capture"
			self.btnCapture.setText(self.captured)

		elif self.captured == "Capture":
			# stop video capture
			self.frmTimer.stop()
			#self.cap.release()
			#self.process_image(self.frame)
			#self.show_image(self.frame)
			self.contourImage.closeCam()
			
			# rotate by 90 degrees
			# frame = cv2.transpose(self.frame)
			frame = self.frame
			frame, edge, contour_img, contours = self.contourImage.getContours(frame)
			print(len(contours))
			# rotate back and flip to get right image
			contour_img_transposed = contour_img
			contour_img_transposed = cv2.transpose(contour_img_transposed)
			contour_img_flipped = cv2.flip(contour_img_transposed,flipCode=1)
			(h, w, _) = contour_img_transposed.shape
			print('h:{}, w:{}'.format(h, w))
			self.show_image(contour_img_flipped)
			self.draw_contours(contours)
			self.captured = "Reset" 
			self.btnCapture.setText(self.captured)
		else:
			for c in self.c3:
				c.clear()	
			self.path_worker.point_ind = nan
			self.captured = "Camera"
			self.btnCapture.setText(self.captured)
			self.video.clear()
			self.path_worker.cmdTimer.stop()

	def draw_contours(self,contours):
		self.c3 = []
		for cnt in contours:
			# iterate through contours 
			pts = asarray(cnt[:,0])
			pts_x_mm = pts[:,0]/640*(boundXRight-boundXLeft)+boundXLeft
			pts_y_mm = -pts[:,1]/480*(boundYUp-boundYDown)+boundYUp
			pts_mm = stack((pts_x_mm,pts_y_mm),axis=-1)
			self.c3.append(self.grpPlot.plot(pts_x_mm,pts_y_mm))

	# def process_image(self,image):
	#	# rotate image by 90 degrees
	#	image = cv2.transpose(image)
	#	
	#	kernel = ones((5,5),float32)/25
	#	filtered = cv2.filter2D(image,-1,kernel)
	#	gray = cv2.cvtColor(filtered,cv2.COLOR_BGR2GRAY)
	#	# create empty image
	#	height, width = gray.shape
	#	image = zeros((height,width,3),uint8)
	#	#Create default parametrization LSD
	#	lsd = cv2.createLineSegmentDetector(0)
	#	lines = lsd.detect(gray)[0]
	#	sp = [] # starting points
	#	tp = [] # target points
	#	# iterate through lines
	#	self.c3 = []
	#	for line in lines:
	#		pts = line[0]
	#		pt1 = (int(pts[0]),int(pts[1]))
	#		pt2 = (int(pts[2]),int(pts[3]))
	#		dist = sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)
	#		if (dist < 20):
	#			continue

	#		pt1_mm = [pt1[0]/640*(boundXRight-boundXLeft)+boundXLeft,-pt1[1]/480*(boundYUp-boundYDown)+boundYUp]
	#		pt2_mm = [pt2[0]/640*(boundXRight-boundXLeft)+boundXLeft,-pt2[1]/480*(boundYUp-boundYDown)+boundYUp]
	#		# if (pt1_mm[0]<-37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
	#		#	pt1_mm[0] = -37
	#		# if (pt1_mm[0]>37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
	#		#	pt1_mm[0] = 37
	#		# if (pt2_mm[0]<-37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
	#		#	pt2_mm[0] = -37
	#		# if (pt2_mm[0]>37 and (pt1_mm[1]>75 or pt1_mm[1]<25)):
	#		#	pt2_mm[0] = 37
	#		sp.append(pt1_mm)
	#		tp.append(pt2_mm)
	#		self.c3.append(self.grpPlot.plot(([pt1_mm[0],pt2_mm[0]]),([pt1_mm[1],pt2_mm[1]])))
	#		## show processed image
	#		#cv2.line(image,pt1,pt2,(0,0,255))

	#	# sketch the lines
	#	self.path_worker.sketch_sig.emit(sp,tp)

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

