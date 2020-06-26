import numpy as np
import scipy.spatial.distance
import cv2
import imutils

import marker

BLUE_MIN = np.array([90, 20, 2])
BLUE_MAX = np.array([130, 255, 255])


def scan(image):
    image_blur = cv2.GaussianBlur(image, (15, 15), 0)

    # cv2.imshow("Blur", image_blur)
    image_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    markers = []

    for contour in contours:
        length = cv2.arcLength(contour, True)

        if length < 50:
            continue

        epsilon = 0.03*length
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 4:
            continue

        distances = []

        for i in range(len(approx)):
            point = approx[i]
            next = approx[(i+1) % 4]
            dist = scipy.spatial.distance.euclidean(point, next)
            distances.append(dist)

        maxDist = 0
        for dist in distances:
            if dist > maxDist:
                maxDist = dist

        for dist in distances:
            # Make sure polygons have reasonable dimensions
            if dist < 0.5*maxDist:
                break
        else:
            # cv2.circle(image, tuple(*approx[0]), 10, (0, 0, 255), 2)

            markers.append(marker.Marker(approx))

    return markers
