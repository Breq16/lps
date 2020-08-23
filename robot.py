import time

import nxt


class Robot:
    FORWARD_SPEED = 50
    TURN_SPEED = 50

    LEFT = -1
    RIGHT = 1

    def __init__(self):
        self.brick = nxt.find_one_brick()
        self.motors = [nxt.Motor(self.brick, nxt.PORT_B),
                       nxt.Motor(self.brick, nxt.PORT_C)]

    def stop(self):
        for motor in self.motors:
            motor.brake()

    def forward(self, secs=None):
        for motor in self.motors:
            motor.run(self.FORWARD_SPEED, regulated=True)

        if secs:
            time.sleep(secs)
            self.stop()

    def turn(self, direction, secs=None):
        self.motors[0].run(direction*self.TURN_SPEED, regulated=True)
        self.motors[1].run(-direction*self.TURN_SPEED, regulated=True)

        if secs:
            time.sleep(secs)
            self.stop()


if __name__ == "__main__":
    r = Robot()
    i = ""
    while i != "q":
        i = input()
        if i == "w":
            r.forward()
        elif i == "s":
            r.stop()
        elif i == "a":
            r.turn(Robot.LEFT)
        elif i == "d":
            r.turn(Robot.RIGHT)
