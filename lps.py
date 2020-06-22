import numpy as np
import cv2


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

    #low_red_mask = cv2.inRange(image_hsv, LOW_RED_MIN, LOW_RED_MAX)
    #high_red_mask = cv2.inRange(image_hsv, HIGH_RED_MIN, HIGH_RED_MAX)
    #mask = low_red_mask + high_red_mask

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)

    cv2.imshow("Frame", image_blur)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
