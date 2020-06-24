import numpy as np
import scipy.spatial.distance
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

def getTransformMatrices(corners, size):
    def mapBasisToPoints(points):
        homoPoints = [np.array([[point[0]], [point[1]], [1]]) for point in points]

        threePoints = np.concatenate(homoPoints[:3], axis=1)

        coefficients = np.matmul(np.linalg.inv(threePoints), homoPoints[3])

        scaled = np.matmul(threePoints, np.array([[coefficients[0][0], 0, 0],
                                                  [0, coefficients[1][0], 0],
                                                  [0, 0, coefficients[2][0]]]))
        return scaled

    sceneCorners = ((-size/2, -size/2), (-size/2, size/2), (size/2, size/2), (size/2, -size/2))

    basisToPicture = mapBasisToPoints(corners)
    basisToScene = mapBasisToPoints(sceneCorners)

    pictureToScene = np.matmul(basisToScene, np.linalg.inv(basisToPicture))
    sceneToPicture = np.matmul(basisToPicture, np.linalg.inv(basisToScene))

    pictureToScene /= pictureToScene[2][2]
    sceneToPicture /= sceneToPicture[2][2]

    return pictureToScene, sceneToPicture

def applyTransform(source_point, matrix):
    homo_source_point = np.array([[coord] for coord in source_point] + [[1]])
    homo_dest_point = np.matmul(matrix, homo_source_point)
    dest_point = (homo_dest_point[0][0] / homo_dest_point[2][0],
                  homo_dest_point[1][0] / homo_dest_point[2][0])
    return dest_point

def matchColor(color):
    colors = {"white": (255, 128, 128),
              "red": (128, 208, 195)}


    minDist = (np.inf, None)

    for (name, ref_color) in colors.items():
        d = scipy.spatial.distance.euclidean(ref_color, color[:3])
        if d < minDist[0]:
            minDist = (d, name)

    return minDist[1]


class Marker:
    def __init__(self, coords):
        self.coords = coords
        self.squares = None

    def getTransformMatrices(self):
        return getTransformMatrices([coord[0] for coord in self.coords], 4)

    def scanSquares(self, image):
        coord_masks = [np.zeros((image.shape[0], image.shape[1], 1), np.uint8) for coord in self.coords]

        # We don't know the orientation of the marker yet without reading the
        # marker squares. But in order to know the marker squares, we need to
        # establish a transform matrix, and in order to do that, we need to know
        # the orientation.

        # The solution to this catch-22 is to pick some orientation arbitrarily,
        # create a "bootstrap" transform matrix, use this to read the squares
        # and determine the orientation, then create the "real" transform matrix.

        pictureToScene, sceneToPicture = self.getTransformMatrices()

        boundary_points_scene = [((-1, -1), (0, -1), (0, 0), (-1, 0)),
                                 ((0, -1), (1, -1), (1, 0), (0, 0)),
                                 ((0, 0), (1, 0), (1, 1), (0, 1)),
                                 ((-1, 0), (0, 0), (0, 1), (-1, 1))]

        boundary_points = []
        for square in boundary_points_scene:
            boundary_points_square = []
            for scene_point in square:
                picture_point = applyTransform(scene_point, sceneToPicture)
                # homo_scene_point = np.array([[coord] for coord in scene_point] + [[1]])
                # homo_picture_point = np.matmul(sceneToPicture, homo_scene_point)
                # picture_point = (int(homo_picture_point[0][0] / homo_picture_point[2][0]),
                #                  int(homo_picture_point[1][0] / homo_picture_point[2][0]))
                boundary_points_square.append(tuple(int(coord) for coord in picture_point))
            boundary_points.append(boundary_points_square)

        #for points in boundary_points:
        #    for point in points:
        #        cv2.circle(image, tuple(int(coord) for coord in point), 10, (255, 0, 255))

        # Now, we can generate masks for each of the four squares.

        for i in range(4):
            points_array = np.array(boundary_points[i])
            cv2.fillPoly(coord_masks[i], [points_array], 255)

        # and determine the color of each.

        image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        self.squares = []
        for i in range(4):
            mean = cv2.mean(image_lab, coord_masks[i])
            self.squares.append(matchColor(mean))

    def findType(self):
        if self.squares.count("red") == 1 and self.squares.count("white") == 3:
            self.type = "target"
            first_corner_index = self.squares.index("red")
        elif self.squares.count("red") == 3 and self.squares.count("white") == 1:
            self.type = "reference"
            first_corner_index = self.squares.index("white")
        else:
            self.type = "none"
            first_corner_index = 0
        self.coords = np.concatenate((self.coords[first_corner_index:], self.coords[:first_corner_index]))
        self.squares = self.squares[first_corner_index:] + self.squares[:first_corner_index]

    def getPicturePos(self):
        pictureToScene, sceneToPicture = self.getTransformMatrices()
        return applyTransform((0, 0), sceneToPicture)
        #return self.coords[0][0]

    def getGlobalPos(self, pictureToScene):
        return applyTransform(self.getPicturePos(), pictureToScene)


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

        #cv2.circle(image, tuple(*approx[0]), 10, (0, 0, 255), 2)

        markers.append(Marker(approx))

    return markers


while True:
    _, image = cap.read()

    # Detect markers by their blue outlines

    markers = findMarkers(image)

    # Detect red squares within markers

    for marker in markers:
        marker.scanSquares(image)
        marker.findType()

    # Sort markers into reference and targets based on number of red squares

    reference = None

    for marker in markers:
        if marker.type == "reference":
            reference = marker
            break

    # Construct projective transform (TODO)
    if reference is not None:
        pictureToScene, sceneToPicture = reference.getTransformMatrices()

    # show marker types and locations
    for marker in markers:
        picture_pos = marker.getPicturePos()

        if reference is not None:
            global_pos = tuple(int(coord) for coord in marker.getGlobalPos(pictureToScene))
        else:
            global_pos = "NO REF"
            print(marker.squares)

        cv2.putText(image, f"{global_pos}:{marker.type}:{marker.squares}", tuple(int(coord) for coord in picture_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 255), 3)

    cv2.imshow("Frame", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
