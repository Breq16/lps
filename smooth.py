import time
import string

import scipy.spatial.distance
import numpy as np
import cv2

targets = {}
target_timestamps = {}
next_letter = "A"

labels = {}
label_timestamps = {}


def smooth_pos(old_pos, new_pos):
    OLD_F = 0.9
    NEW_F = 1 - OLD_F
    return ((OLD_F*old_pos[0] + NEW_F*new_pos[0]),
            (OLD_F*old_pos[1] + NEW_F*new_pos[1]))


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
                                                    target)
            if dist < smallest_dist:
                smallest_dist = dist
                closest_target = letter

        if closest_target is None:
            closest_target = target_letter()
            targets[closest_target] = marker.global_pos()
        else:
            targets[closest_target] = smooth_pos(targets[closest_target],
                                                 marker.global_pos())
        target_timestamps[closest_target] = time.time()

    elif marker.type == "label":
        if marker.num in labels:
            labels[marker.num] = smooth_pos(labels[marker.num],
                                            marker.global_pos())
        else:
            labels[marker.num] = marker.global_pos()
        label_timestamps[marker.num] = time.time()


def prune(threshold=0.2):
    global targets, labels
    now = time.time()

    dead_targets = []
    for letter, timestamp in target_timestamps.items():
        if now - timestamp > threshold:
            dead_targets.append(letter)

    for letter in dead_targets:
        del targets[letter]
        del target_timestamps[letter]

    dead_labels = []
    for num, timestamp in label_timestamps.items():
        if now - timestamp > threshold:
            dead_labels.append(num)

    for num in dead_labels:
        del labels[num]
        del label_timestamps[num]


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

    for letter, pos in targets.items():
        if pos is not None:
            cv2.circle(image, coord_to_px(pos), 10, (0, 255, 255))
            cv2.putText(image, str(letter), coord_to_px(pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)

    for num, pos in labels.items():
        if pos is not None:
            cv2.circle(image, coord_to_px(pos), 10, (255, 255, 0))
            cv2.putText(image, str(num), coord_to_px(pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)

    return image


def dump():
    global targets, labels
    return {"targets": targets, "labels": labels}
