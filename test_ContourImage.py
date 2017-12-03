import cv2
import numpy as np
import ContourImage

def main():
    contour_image = ContourImage.ContourImage()
    while(True):
        (frame, edge, contours) = contour_image.getContours()
        (height, width) = edge.shape
        contour_canvas = np.zeros([height, width, 3], dtype=np.uint8)

        cv2.imshow('frame',frame)
        cv2.imshow('edge',edge)

        for cnt in contours:
            cv2.drawContours(contour_canvas, [cnt],  0, (0, 255, 0), 3)

        cv2.imshow('contours', contour_canvas)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    main()