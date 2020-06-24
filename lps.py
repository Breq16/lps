import numpy as np
import cv2
import imutils


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)

BLUE_MIN = np.array([90, 20, 2])
BLUE_MAX = np.array([130, 255, 255])

def lineIntersect(a, b, c, d):
    ab = np.linalg.det(np.array([a, b]))
    cd = np.linalg.det(np.array([c, d]))
    abx = np.linalg.det(np.array([[a[0], 1], [b[0], 1]]))
    cdx = np.linalg.det(np.array([[c[0], 1], [d[0], 1]]))
    aby = np.linalg.det(np.array([[a[1], 1], [b[1], 1]]))
    cdy = np.linalg.det(np.array([[c[1], 1], [d[1], 1]]))

    xnum = np.linalg.det(np.array([[ab, abx], [cd, cdx]]))
    ynum = np.linalg.det(np.array([[ab, aby], [cd, cdy]]))
    denom = np.linalg.det(np.array([[abx, aby], [cdx, cdy]]))

    return (xnum / denom, ynum / denom)

def getGridPosition(corners, x, y):
    return lineIntersect((1-y)*corners[0][0]+y*corners[3][0],
                         (1-y)*corners[1][0]+y*corners[2][0],
                         (1-x)*corners[0][0]+x*corners[1][0],
                         (1-x)*corners[3][0]+x*corners[2][0])

class Marker:
    def __init__(self, coords):
        self.coords = coords
        self.squares = None

    def scanSquares(self, image):
        coord_masks = [np.zeros((image.shape[0], image.shape[1], 1), np.uint8) for coord in self.coords]

        boundary_points = []
        for i in range(4):
            # Find boundary points
            ordered_corners = np.concatenate((self.coords[i:], self.coords[:i]))
            boundary_points.append([getGridPosition(ordered_corners, 1/4, 1/4),
                                    getGridPosition(ordered_corners, 1/2, 1/4),
                                    getGridPosition(ordered_corners, 1/2, 1/2),
                                    getGridPosition(ordered_corners, 1/4, 1/2)])

        for points in boundary_points:
            for point in points:
                cv2.circle(image, tuple(int(coord) for coord in point), 10, (255, 0, 255))


        #cv2.fillPoly(roi_mask, [marker.coords], 255)
        #cv2.imshow("Marker Mask", roi_mask)

        # marker_image = cv2.bitwise_and(image, image, mask=roi_mask)
        # marker_image_hsv = cv2.cvtColor(marker_image, cv2.COLOR_BGR2HSV)
        #
        # #cv2.imshow("Squares", marker_image)
        #
        # low_red_mask = cv2.inRange(marker_image_hsv, LOW_RED_MIN, LOW_RED_MAX)
        # high_red_mask = cv2.inRange(marker_image_hsv, HIGH_RED_MIN, HIGH_RED_MAX)
        # red_mask = low_red_mask + high_red_mask
        #
        # #cv2.imshow("Red Mask", red_mask)
        #
        # contours = cv2.findContours(red_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # contours = imutils.grab_contours(contours)
        #
        # self.squares = []
        #
        # for contour in contours:
        #     length = cv2.arcLength(contour, True)
        #
        #     #if length < 20:
        #     #    continue
        #
        #     epsilon = 0.1*length
        #     approx = cv2.approxPolyDP(contour, epsilon, True)
        #
        #     #if len(approx) != 4:
        #     #    continue
        #
        #     cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        #     cv2.drawContours(image, [approx], -1, (255, 0, 255), 2)
        #
        #     self.squares.append(approx)

def findMarkers(image):
    image_blur = cv2.GaussianBlur(image, (5, 5), 0)
    image_hsv = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_hsv, BLUE_MIN, BLUE_MAX)

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    markers = []

    for contour in contours:
        length = cv2.arcLength(contour, True)

        if length < 100:
            continue

        epsilon = 0.02*length
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) != 4:
            continue

        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        cv2.drawContours(image, [approx], -1, (255, 0, 0), 2)

        markers.append(Marker(approx))

    return markers


while True:
    _, image = cap.read()

    # Detect markers by their blue outlines

    markers = findMarkers(image)

    # Detect red squares within markers

    for marker in markers:
        marker.scanSquares(image)

    # Sort markers into reference and targets based on number of red squares

    #reference = None

    #for marker in markers:
    #    if marker.getType() == 3:
    #        reference = marker
    #        break

    # Determine orientation of markers based on position of centroid of red squares relative to position of centroid of blue outline (TODO)

    #if reference is not None:
    #    reference.findReferenceHeading()

    # Construct projective transform (TODO)


    cv2.imshow("Frame", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
