import numpy as np
import scipy.spatial.distance
import cv2
import imutils

import marker
import gui

BLUE_MIN = np.array([90, 40, 100])
BLUE_MAX = np.array([120, 255, 255])


def scan(image):
    "Scan an image for markers."
    image_blur = cv2.GaussianBlur(image, (15, 15), 0)

    image_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)
    gui.show(image_hsv, "camera_hsv")

    image_gray = cv2.cvtColor(image_blur, cv2.COLOR_BGR2GRAY)
    gui.show(image_gray, "camera_gray")

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)
    gui.show(mask, "mask_border")

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    markers = []

    mask_with_contours = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    image_with_contours = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    cv2.drawContours(mask_with_contours, contours, -1, (0, 255, 0), 2)
    cv2.drawContours(image_with_contours, contours, -1, (0, 255, 0), 2)

    gui.show(mask_with_contours, "mask_border_contours")
    gui.show(image_with_contours, "camera_border_contours")

    image_with_approx = image_with_contours.copy()

    for contour in contours:

        length = cv2.arcLength(contour, True)

        if length < 20:
            continue

        epsilon = 0.05*length
        approx = cv2.approxPolyDP(contour, epsilon, True)

        cv2.polylines(image_with_approx, [approx], True, (255, 0, 0), 2)

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
            if dist < 0.3*maxDist:
                break
        else:
            new_marker = marker.Marker(image_gray,
                                       [[int(coord) for coord in column[0]]
                                        for column in approx])
            if new_marker.is_valid:
                markers.append(new_marker)

    gui.show(image_with_approx, "camera_border_approx")
    return markers
