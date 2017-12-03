import cv2
import numpy as np

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while (True):
	ret, frame = cap.read()
	kernel = np.ones((5,5),np.uint8)
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray,(5,5),0)
	
	# cannyedge detection
	edge = cv2.Canny(gray,30,150)
	cv2.imshow("canny edge",edge)
	
	# find contour
	img,contours,hierarchy = cv2.findContours(edge,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	height, width = img.shape
	blank = np.zeros([height,width,3],dtype=np.uint8)
	for cnt in contours:
		#if cv2.contourArea(cnt)>100 and cv2.arcLength(cnt,True) > 500:
		cv2.drawContours(blank, [cnt],0, (0,255,0), 3)
	
	img = blank
	# face detection
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	for (x,y,w,h) in faces:
    		cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    		roi_gray = gray[y:y+h, x:x+w]
    		roi_color = blank[y:y+h, x:x+w]

	cv2.imshow('contour_edge',img)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
