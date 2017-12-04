import cv2
import numpy as np

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while (True):
    ret, frame = cap.read()
    kernel = np.ones((5, 5), np.uint8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # cannyedge detection
    edge = cv2.Canny(gray, 30, 150)
    cv2.imshow("canny edge", edge)

    # set up blank images
    height, width = edge.shape
    blank = np.zeros([height, width, 3], dtype=np.uint8)
    portrait_img = np.zeros([height, width, 3], dtype=np.uint8)
    merged_img = np.zeros([height, width, 3], dtype=np.uint8)
    portrait = np.zeros((height, width),dtype=np.uint8)

    img = blank
    offset = 20
    # face detection
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        x -= offset
        y -= (int)(3.5*offset)
        w += 2*offset
        h += (int)(3.5*offset)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = blank[y:y + h, x:x + w]

        # cv2.imshow('contour_edge', img)

        # crop portrait
        tmp = edge[y:y + h, x:x + w]
        # print(tmp.shape + " | " + w + h)
        if tmp.shape == (h, w):
            portrait[y:y + h, x:x + w] = tmp
            edge[y:y + h, x:x + w] = np.zeros((h,w))

        # img, contours, hierarchy = cv2.findContours(
        #     portrait, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find contour outside portrait
    img, contours, hierarchy = cv2.findContours(
        edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # filter out short contours and plot
    canvas_contours = list()
    for cnt in contours:
        if cv2.contourArea(cnt)>70 and cv2.arcLength(cnt,True) > 400:
            cv2.drawContours(blank, [cnt], 0, (0, 255, 0), 3)
            canvas_contours.append(cnt)

    img = blank
    cv2.imshow('contour_edge', img)

    # find contour inside portrait
    img, portrait_contours, hierarchy = cv2.findContours(
        portrait, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in portrait_contours:
        cv2.drawContours(portrait_img, [cnt], 0, (0, 255, 0), 3)
    cv2.imshow('portrait contour', portrait_img)

    # merge contours
    merged_contours = canvas_contours + portrait_contours
    for cnt in merged_contours:
        cv2.drawContours(merged_img, [cnt], 0, (0, 255, 0), 3)
    cv2.imshow('merged contours', merged_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
