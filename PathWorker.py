from __init__ import * 

class PathWorker(QObject):
	plot_sig = pyqtSignal(float,float,int,int)
	text_sig = pyqtSignal(str,str)
	generate_sig = pyqtSignal(int,int)
	serial_sig = pyqtSignal()
	sketch_sig = pyqtSignal(list,list)
	moved_sig = pyqtSignal()
	def __init__(self,sx,sy):
		super(PathWorker,self).__init__()

		# setup serial
		self.serial_sig.connect(self.serial_change)
		self.ser_flag = False
		self.ser_port = '/dev/ttyACM0'
		self.startByte = 0xff.to_bytes(1, byteorder="little", signed=False)
		self.endByte = 0x00.to_bytes(1, byteorder="little", signed=False)

		# set up initial lift position
		self.lift = 0x00
		self.liftWaitFlag = True

		# setup generate path
		self.generate_sig.connect(self.generate_path)
		self.x0 = sx
		self.y0 = sy

		# set servo to inital position
		degLeft,degRight,servoLeft,servoRight = inv_kinematics(self.x0,self.y0)
		self.send_command(servoLeft,servoRight)

		# setup control timer for sending bytes and update graph
		self.cmdTimer = QTimer()
		self.cmdTimer.timeout.connect(self.move_path)
		self.cmdTimerPeriod = 50

		# setup sketch image
		self.sketch_sig.connect(self.sketch_image)
		self.moved_sig.connect(self.sketch_next_point)
		self.point_ind = nan

	def generate_path(self,x,y):
		increment = 0.3 
		dx = x- self.x0
		dy = y- self.y0
		c = sqrt(dx**2+dy**2)
		self.steps = int(c/increment)
		self.step_ind = 0
		try:
			self.dx = dx/self.steps
			self.dy = dy/self.steps
			self.cmdTimer.start(self.cmdTimerPeriod)
		except ZeroDivisionError:
			if not math.isnan(self.point_ind):
				self.moved_sig.emit()
			return

	def move_path(self):
		# target positions
		tx = self.x0+self.dx
		ty = self.y0+self.dy
		degLeft,degRight,servoLeft,servoRight = inv_kinematics(tx,ty)
		# print (servoLeft, servoRight)

		# check if solution is valid
		if math.isnan(servoLeft) or math.isnan(servoRight):
			print("Position cannot be reached")
			self.cmdTimer.stop()
			# TODO: might not work, try to force continue if position cannot reach
			if not math.isnan(self.point_ind):
				self.moved_sig.emit()
		else:
			# update current values
			self.x0 = tx
			self.y0 = ty
			print (self.x0,self.y0)
			self.servoLeft = servoLeft
			self.servoRight = servoRight

			# send command to arduino			
			self.send_command(servoLeft,servoRight)

			# update GUI
			self.text_sig.emit("{:10.2f}".format(degLeft),"{:10.2f}".format(degRight))
			# update plot
			self.plot_sig.emit(degLeft,degRight,tx,ty)
		# increase current index
		self.step_ind += 1
		if self.step_ind == self.steps:
			self.cmdTimer.stop()
			if not math.isnan(self.point_ind):
				self.moved_sig.emit()

	def sketch_image(self,sp,tp):
		print ("sketch image")
		self.point_ind = 0
		self.start_point = True
		self.start = sp 
		self.target = tp
		# input("press enter to continue")
		self.sketch_next_point()

	def sketch_next_point(self):
		print (self.point_ind,len(self.start))
		if self.point_ind >= len(self.start):
			print ("finish sketching")
			self.point_ind = nan
			return
		if self.start_point == True:	# generate traj for start point, lift arms
			pt = self.start[self.point_ind]
			print ("lift")
			self.lift = 0x01
			# self.cmdTimer.stop()
			# time.sleep(2)
			# self.cmdTimer.start(self.cmdTimerPeriod)
			self.liftWaitFlag = True
			print("awake")
			self.start_point = False
		elif self.start_point == False:	# generate traj for target point, lower arms
			pt = self.target[self.point_ind]
			print ("down")
			self.lift = 0x00
			# self.cmdTimer.stop()
			# time.sleep(2)
			# self.cmdTimer.start(self.cmdTimerPeriod)
			self.liftWaitFlag = True
			print ("awake")
			self.start_point = True
			# increase index to next point
			self.point_ind += 1
		if self.liftWaitFlag == True:
			time.sleep(0.2)
			self.send_command(self.servoLeft, self.servoRight)
			time.sleep(0.8)
		self.generate_path(pt[0],pt[1])

	def send_command(self,servoLeft,servoRight):
		# convert double to int
		servoLeft = int(servoLeft)
		servoRight = int(servoRight)

		# Create four bytes from the integer 
		servoLeft_bytes = servoLeft.to_bytes(2, byteorder='big', signed=False)
		servoRight_bytes = servoRight.to_bytes(2, byteorder='big', signed=False)
		self.set_end_byte(servoLeft_bytes, servoRight_bytes)
		# print(self.startByte, servoLeft_bytes, servoRight_bytes, self.endByte)

		# send command to arduino
		if self.ser_flag:
			self.ser.write(self.startByte)
			self.ser.write(servoLeft_bytes)
			self.ser.write(servoRight_bytes)
			self.ser.write(self.lift.to_bytes(1, byteorder="little", signed=False))
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

	def serial_change(self):
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

if __name__ == "__main__":
	pathworker = PathWorker(1,2,3,4)
	print ("This is path worker")
