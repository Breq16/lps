import time

import nxt


FORWARD_SPEED = 50
TURN_SPEED = 50

LEFT = -1
RIGHT = 1


brick = nxt.find_one_brick()
motors = [nxt.Motor(brick, nxt.PORT_B),
          nxt.Motor(brick, nxt.PORT_C)]


def stop(secs=0.2):
    for motor in motors:
        motor.idle()
    if secs:
        time.sleep(secs)


def forward(secs=0.2):
    for motor in motors:
        motor.run(FORWARD_SPEED, regulated=True)

    if secs:
        time.sleep(secs)
        stop(0)


def turn(direction, secs=0.2):
    motors[0].run(-direction*TURN_SPEED, regulated=True)
    motors[1].run(direction*TURN_SPEED, regulated=True)

    if secs:
        time.sleep(secs)
        stop(0)


def action(word):
    if word == "forward":
        forward()
    elif word == "left":
        turn(LEFT)
    elif word == "right":
        turn(RIGHT)
    elif word == "stop":
        stop()


if __name__ == "__main__":
    i = ""
    while i != "q":
        i = input()
        if i == "w":
            forward()
        elif i == "s":
            stop()
        elif i == "a":
            turn(LEFT)
        elif i == "d":
            turn(RIGHT)
