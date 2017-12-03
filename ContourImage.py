import cv2
import numpy as np

class ContourImage(object):
	def __init__(self):
		'''
		initialize opencv
		'''
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		print("init facecascade calssifier: {}".format(self.face_cascade))

	def __del__(self):
		'''
		destructor
		close VideoCapture
		destroys all windows
		:return:
		'''
		self.cap.release()
		#cv2.destroyAllWindows()

	def openCam(self):
		'''
		open camera
		'''
		self.cap = cv2.VideoCapture(0)
		# self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	def closeCam(self):
		self.cap.release()

	def returnFrame(self):
		ret,self.frame = self.cap.read()
		return self.frame

	def getContours(self,img):
		'''

		:param img: non-transposed img
		:return:
		'''
		
		frame = img 
		#ret, frame = self.cap.read()
		kernel = np.ones((5, 5), np.uint8)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(gray, (5, 5), 0)

		# cannyedge detection
		edge = cv2.Canny(gray, 30, 150)
		# cv2.imshow("canny edge", edge)

		# set up blank images
		height, width = edge.shape
		blank = np.zeros([height, width, 3], dtype=np.uint8)
		portrait_img = np.zeros([height, width, 3], dtype=np.uint8)
		merged_img = np.zeros([height, width, 3], dtype=np.uint8)
		portrait = np.zeros((height, width), dtype=np.uint8)

		img = blank
		offset = 20
		# face detection
		print(self.face_cascade.getOriginalWindowSize())
		faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
		print("num of faces: {}".format(len(faces)))
		for (x, y, w, h) in faces:
			x -= offset
			y -= (int)(2.5 * offset)
			w += 2 * offset
			h += (int)(3.5 * offset)
			cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
			roi_gray = gray[y:y + h, x:x + w]
			roi_color = blank[y:y + h, x:x + w]

			# crop portrait
			tmp = edge[y:y + h, x:x + w]
			# print(tmp.shape + " | " + w + h)
			if tmp.shape == (h, w):
				portrait[y:y + h, x:x + w] = tmp
				edge[y:y + h, x:x + w] = np.zeros((h, w))

			# img, contours, hierarchy = cv2.findContours(
			#	  portrait, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# transpose edge
		edge = cv2.transpose(edge)

		# find contour outside portrait
		img, contours, hierarchy = cv2.findContours(
			edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		# filter out short contours and plot
		canvas_contours = list()
		for cnt in contours:
			if cv2.contourArea(cnt) > 70 and cv2.arcLength(cnt, True) > 400:
				cv2.drawContours(blank, [cnt], 0, (0, 255, 0), 3)
				canvas_contours.append(cnt)

		img = blank
		# cv2.imshow('contour_edge', img)

		# transpose portrait
		portrait = cv2.transpose(portrait)

		# find contour inside portrait
		img, portrait_contours, hierarchy = cv2.findContours(
			portrait, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		for cnt in portrait_contours:
			if cv2.contourArea(cnt) > 10:
				cv2.drawContours(portrait_img, [cnt], 0, (0, 255, 0), 3)
		# cv2.imshow('portrait contour', portrait_img)

		# merge contours
		merged_contours = canvas_contours + portrait_contours
		for cnt in merged_contours:
			cv2.drawContours(merged_img, [cnt], 0, (0, 255, 0), 3)
		# cv2.imshow('merged contours', merged_img)
		print("merged contours: {}".format(len(merged_contours)))

		return (frame, edge, merged_img, merged_contours)
