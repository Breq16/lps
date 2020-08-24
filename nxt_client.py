import math
import time

import client
import robot

MY_NUM = "0"
TARGET_NUM = "1"


class Bounds:
    MAX_DISTANCE = 8
    MIN_DISTANCE = 7
    MAX_ANGLE = math.pi / 3
    MIN_ANGLE = math.pi / 6


def next_action(my_pose, target_pose, prev_action):
    my_pos = my_pose["center"]
    target = target_pose["center"]

    offset = [target[i] - my_pos[i] for i in range(2)]

    global_angle = math.atan2(offset[1], offset[0])
    relative_angle = global_angle - my_pose["heading"]

    if relative_angle > math.pi:
        relative_angle -= 2*math.pi
    if relative_angle < -math.pi:
        relative_angle += 2*math.pi

    distance = math.sqrt(offset[0]**2 + offset[1]**2)

    print(f"Offset: {offset[0]}, {offset[1]}")
    print(f"Dist: {distance}, Heading: {relative_angle}")

    if prev_action == "forward":
        if distance < Bounds.MIN_DISTANCE:
            # Stop moving forward if we are too close
            return "stop"
        else:
            # Otherwise keep moving, we are far away
            if abs(relative_angle) > Bounds.MAX_ANGLE:
                # Turn, we are pointed the wrong way
                if relative_angle > 0:
                    return "left"
                else:
                    return "right"
            else:
                return "forward"
    elif prev_action == "stop":
        if distance < Bounds.MAX_DISTANCE:
            # Keep staying still, we are close
            return "stop"
        else:
            # We need to move, we are far away
            if abs(relative_angle) > Bounds.MAX_ANGLE:
                # Turn, we are pointed the wrong way
                if relative_angle > 0:
                    return "left"
                else:
                    return "right"
            else:
                return "forward"
    elif prev_action in ("left", "right"):
        if abs(relative_angle) > Bounds.MIN_ANGLE:
            # We need to keep turning
            if relative_angle > 0:
                return "left"
            else:
                return "right"
        else:
            # We can stop turning now
            if distance > Bounds.MAX_DISTANCE:
                # But we need to move closer
                return "forward"
            else:
                # We are close enough
                return "stop"


action = "stop"

while True:
    state = client.get_state()

    if MY_NUM not in state["labels"] or TARGET_NUM not in state["labels"]:
        continue

    my_pose = state["labels"][MY_NUM]
    target_pose = state["labels"][TARGET_NUM]

    action = next_action(my_pose, target_pose, action)

    print(action)

    robot.action(action)
    time.sleep(0.2)
