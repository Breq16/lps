import time
import string

import scipy.spatial.distance
import numpy as np
import cv2

targets = {}
next_letter = "A"

labels = {}


def target_letter():
    global next_letter
    if next_letter is not None and next_letter not in targets.keys():
        letter = next_letter
        if next_letter != "Z":
            next_letter = chr(ord(next_letter) + 1)
        else:
            next_letter = "A"
        return letter

    for letter in string.ascii_uppercase:
        if letter not in targets.keys():
            return letter


def register(marker):
    global targets, labels

    if marker.global_pos() is None:
        return

    if marker.type == "target":
        # attempt to match to an existing target
        smallest_dist = 2
        closest_target = None

        for letter, target in targets.items():
            dist = scipy.spatial.distance.euclidean(marker.global_pos(),
                                                    target.global_pos())
            if dist < smallest_dist:
                smallest_dist = dist
                closest_target = letter

        if closest_target is None:
            closest_target = target_letter()
        targets[closest_target] = marker

    elif marker.type == "label":
        labels[marker.num] = marker


def prune(threshold=0.2):
    global targets, labels
    now = time.time()

    dead_targets = []
    for letter, target in targets.items():
        if now - target.timestamp > threshold:
            print(f"purging {letter}")
            dead_targets.append(letter)

    for letter in dead_targets:
        del targets[letter]

    dead_labels = []
    for label in labels.values():
        if now - label.timestamp > threshold:
            dead_labels.append(label.num)

    for num in dead_labels:
        del labels[num]


def render():
    image = np.zeros((500, 500, 3), np.uint8)

    def coord_to_px(pos):
        x = image.shape[1]/2 + pos[0]*20 + 10
        y = image.shape[1]/2 - pos[1]*20 - 10
        return (int(round(x)), int(round(y)))

    # Draw X/Y axes
    cv2.arrowedLine(image, coord_to_px((0, 0)), coord_to_px((0, 3)),
                    (255, 0, 0), 2)
    cv2.arrowedLine(image, coord_to_px((0, 0)), coord_to_px((3, 0)),
                    (0, 255, 0), 2)

    for letter, target in targets.items():
        pos = target.global_pos()
        if pos is not None:
            cv2.circle(image, coord_to_px(pos), 10, (0, 255, 255))
            cv2.putText(image, str(letter), coord_to_px(pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)

    for label in labels.values():
        pos = label.global_pos()
        if pos is not None:
            cv2.circle(image, coord_to_px(pos), 10, (255, 255, 0))
            cv2.putText(image, str(label.num), coord_to_px(pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)

    return image
