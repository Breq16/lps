import numpy as np
import cv2
import imutils


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)

LOW_RED_MIN = np.array([0, 120, 70])
LOW_RED_MAX = np.array([10, 255, 255])

HIGH_RED_MIN = np.array([170, 120, 70])
HIGH_RED_MAX = np.array([180, 120, 70])

BLUE_MIN = np.array([94, 80, 2])
BLUE_MAX = np.array([126, 255, 255])

while True:
    _, image = cap.read()

    image_blur = cv2.GaussianBlur(image, (5, 5), 0)
    image_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    for contour in contours:
        length = cv2.arcLength(contour, True)

        if length < 100:
            continue

        epsilon = 0.02*length
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 6:
            continue

        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        cv2.drawContours(image, [approx], -1, (255, 0, 0), 2)

        largestDist = (approx[0][0], 0)

        for i in range(len(approx)):
            prev = approx[i][0]
            i += 1
            if i == len(approx):
                i = 0
            current = approx[i][0]
            i += 1
            if i == len(approx):
                i = 0
            next = approx[i][0]

            prevDist = np.linalg.norm(prev-current)
            nextDist = np.linalg.norm(next-current)
            dist = prevDist + nextDist

            if dist > largestDist[1]:
                largestDist = (current, dist)

        cv2.circle(image, tuple(int(coord) for coord in largestDist[0]), 10, (255, 0, 255), 2)


    cv2.imshow("Frame", image)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
