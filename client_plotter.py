import requests
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 240))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    resp = requests.get("http://localhost:5000/markers").json()
    print(resp)

    screen.fill((0, 0, 0))
    for marker in resp:
        pygame.draw.circle(screen, (255, 255, 255), marker["pos"], 10)
    pygame.display.update()
    input()
