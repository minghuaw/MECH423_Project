import cv2
import numpy as np
import ContourImage

def main():
	contour_image = ContourImage.ContourImage()
	contour_image.openCam()

	while(True):
		frame = contour_image.returnFrame()
		(frame, edge, merged_img, contours) = contour_image.getContours(frame)
		(height, width) = edge.shape
		contour_canvas = np.zeros([height, width, 3], dtype=np.uint8)
		point_canvas = np.zeros([height, width, 3], dtype=np.uint8)

		cv2.imshow('frame',frame)
		cv2.imshow('edge',edge)

		print(len(contours))
		for cnt in contours:
			cv2.drawContours(contour_canvas, [cnt],  0, (0, 255, 0), 3)

			if cv2.waitKey(0) & 0xFF == ord('n'):
				if cv2.contourArea(cnt) > 10:
					cv2.polylines(point_canvas,[cnt],True,(0,255,255))
					cv2.imshow('points', point_canvas)
				cv2.imshow('contours', contour_canvas)
			else:
				break
		if cv2.waitKey(0) & 0xFF == ord('q'):
			break

	contour_image.closeCam()

if __name__ == '__main__':
	main()
