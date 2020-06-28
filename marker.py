import numpy as np
import cv2
import scipy.spatial.distance

import transform


def match_color(color):
    "Determine if a color is closer to green or red."
    colors = {"green": (182, 76, 196),
              "red": (164, 187, 151)}

    min_dist = np.inf
    match = None

    for (name, ref_color) in colors.items():
        d = scipy.spatial.distance.euclidean(ref_color, color[:3])
        if d < min_dist:
            min_dist = d
            match = name

    return match


class Marker:
    "Representation of a single tracking marker."

    def __init__(self, corners):
        "Initialize a Marker with corners at the given positions."
        self.corners = corners
        self.squares = None

    def calc_transform(self):
        """Calculate the transformation matrices between the Marker's position
        on the picture and its position in the scene."""

        self.pic_to_scene, self.scene_to_pic = transform.get_matrices(
            self.corners, 4)

    def scan_square(self, image_lab, pos):
        """Identify the color of a square at the given position relative to the
        origin of the marker."""

        boundary_points = (
            (pos[0], pos[1]),
            (pos[0]-1, pos[1]),
            (pos[0]-1, pos[1]-1),
            (pos[0], pos[1]-1)
        )

        coord_mask = np.zeros((image_lab.shape[0], image_lab.shape[1], 1),
                              np.uint8)

        picture_points = np.array(tuple(self.pic_pos(point)
                                        for point in boundary_points), np.intc)

        cv2.fillPoly(coord_mask, [picture_points], 255)

        mean_color = cv2.mean(image_lab, coord_mask)
        return match_color(mean_color)

    def scan(self, image):
        "Scan the Marker's squares to determine its orientation and type."
        self.calc_transform()

        image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # We don't know the orientation of the marker yet without reading the
        # marker squares. But in order to know the marker squares, we need to
        # establish a transform matrix, and in order to do that, we need to
        # know the orientation.

        # The solution to this catch-22 is to pick some orientation
        # arbitrarily, create a "bootstrap" transform matrix, use this to read
        # the squares and determine the orientation, then create the "real"
        # transform matrix.

        square_positions = ((1, 1), (0, 1), (0, 0), (1, 0))

        self.squares = list(self.scan_square(image_lab, pos)
                            for pos in square_positions)

        # Use the information gathered from the squares to interpret the type
        # of this marker

        if self.squares.count("red") == 1:
            self.type = "target"
            first_corner_index = self.squares.index("red")
        elif self.squares.count("red") == 2:
            self.type = "label"
            if self.squares[0] == "red" and self.squares[3] == "red":
                first_corner_index = 3
            else:
                first_corner_index = self.squares.index("red")
        elif self.squares.count("red") == 3:
            self.type = "reference"
            for i, square in enumerate(self.squares):
                if square != "red":
                    first_corner_index = i
                    break
        else:
            self.type = "none"
            first_corner_index = 0

        self.corners = (self.corners[first_corner_index:]
                        + self.corners[:first_corner_index])
        self.squares = (self.squares[first_corner_index:]
                        + self.squares[:first_corner_index])

        # Now that we have the orientation, recalculate the transform matrices
        self.calc_transform()

        # Read any auxillary squares present
        more_squares = (self.type == "label")
        row = 0

        self.aux_squares = []

        while more_squares:
            aux_square_positions = tuple((-1+col, -2-row) for col in range(4))

            row_squares = list(self.scan_square(image_lab, pos)
                               for pos in aux_square_positions)

            self.aux_squares.append(row_squares)
            more_squares = (row_squares[0] == "green")

            row += 1
            if row >= 4:  # sanity check
                break

        aux_data = []
        for aux_row in self.aux_squares:
            for aux_square in aux_row[1:]:
                aux_data.append(aux_square == "red")

        if len(self.aux_squares) == 0:
            self.num = -1
        elif len(self.aux_squares) == 1:
            self.num = 0
        elif len(self.aux_squares) == 2:
            self.num = 8
        elif len(self.aux_squares) == 3:
            self.num = 40
        else:
            self.num = 552

        for i, bit in enumerate(aux_data):
            if bit:
                self.num += 2**i

    def pic_pos(self, pos=(0, 0), return_float=False):
        """Map a position in the scene to its position in the picture
        (using this marker as the reference)."""

        pos = transform.apply(pos, self.scene_to_pic)
        if return_float:
            return pos
        else:
            return tuple(int(coord) for coord in pos)

    def scene_pos(self, pos=(0, 0), return_float=True):
        """Map a position in the picture to its position in the scene
        (using this marker as the reference)."""

        pos = transform.apply(pos, self.pic_to_scene)
        if return_float:
            return pos
        else:
            return tuple(int(coord) for coord in pos)

    def scene_pos_marker(self, marker, pos=(0, 0), return_float=True):
        """Get the position of another marker in the scene
        (using this marker as the reference)."""

        pos = marker.pic_pos(pos, True)
        return self.scene_pos(pos, return_float)

    def use_reference(self, reference=None):
        """Set this marker's reference for global position calculation."""
        self.reference = reference

    def global_pos(self, pos=(0, 0), return_float=True):
        "Calculate the global position of this marker using its reference."
        if self.reference is not None:
            return self.reference.scene_pos_marker(self, pos, return_float)
        else:
            return None

    def display(self, image):
        "Draw information about this marker on the image."

        polylines_arr = np.array([self.corners])

        text = []

        if self.type == "reference":
            # Draw border
            cv2.polylines(image, polylines_arr, True, (255, 0, 255), 2)
            # Draw center
            cv2.circle(image, self.pic_pos(), 10, (255, 0, 255), 2)
            # Draw X/Y axes
            cv2.arrowedLine(image, self.pic_pos(),
                            self.pic_pos((3, 0)),
                            (0, 0, 255), 2)
            cv2.arrowedLine(image, self.pic_pos(),
                            self.pic_pos((0, 3)),
                            (0, 255, 0), 2)
        elif self.type == "target" or self.type == "label":
            # Draw border
            cv2.polylines(image, polylines_arr, True, (0, 255, 255), 2)
            # Draw center
            cv2.circle(image, self.pic_pos(), 10, (0, 255, 255), 2)
            # Draw orientation
            cv2.arrowedLine(image, self.pic_pos(),
                            self.pic_pos((0, 2)),
                            (255, 0, 0), 2)
            # Draw position
            global_pos = self.global_pos(return_float=False)
            if global_pos is not None:
                text.append(f"{global_pos}")

            if self.num >= 0:
                text.append(str(self.num))
        else:
            # Draw border
            cv2.polylines(image, polylines_arr, True, (0, 0, 255), 2)
            # Draw center
            cv2.circle(image, self.pic_pos(), 10, (0, 0, 255), 2)
            # Draw squares
            text.append("".join("R" if square == "red" else "G"
                                for square in self.squares))

        text = ":".join(text)
        cv2.putText(image, text, self.pic_pos(),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255, 0), 3)
