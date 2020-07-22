import pygame
import pygame.joystick
import nxt

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

brick = nxt.find_one_brick()

left_motor = nxt.Motor(brick, "B")
right_motor = nxt.Motor(brick, "C")


def clamp(val, range):
    if val < range[0]:
        return range[0]
    if val > range[1]:
        return range[1]
    return val


while True:
    pygame.event.pump()

    speed = -joystick.get_axis(1)
    steer = joystick.get_axis(3)

    left_speed = speed + steer
    right_speed = speed - steer

    left_speed = clamp(left_speed*100, (-100, 100))
    right_speed = clamp(right_speed*100, (-100, 100))

    left_motor.run(left_speed)
    right_motor.run(right_speed)
