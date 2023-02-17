from math import pi

import pygame
from line import Line
from box import Box
from robot import Robot

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


(width, height) = (1920, 1080)
STEP_SIZE = 0.0001


background = WHITE
running = True
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

robby = Robot(screen, direction=pi / 2 * 3)
box = Box(200, 200, 1700, 880)
box.draw(screen)
robby._draw(box.lines())
pygame.display.update()
line = Line(200, 500, 700, 200)
while running:
    screen.fill(background)
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Possible to use something like "last_pos = pygame.mouse.get_pos()"
            pass
        if event.type == pygame.QUIT:
            running = False
    key_event = pygame.key.get_pressed()
    if key_event[pygame.K_o]:
        robby.speed.right += STEP_SIZE
    if key_event[pygame.K_l]:
        robby.speed.right -= STEP_SIZE
    if key_event[pygame.K_w]:
        robby.speed.left += STEP_SIZE
    if key_event[pygame.K_s]:
        robby.speed.left -= STEP_SIZE
    if key_event[pygame.K_t]:
        robby.speed.left += STEP_SIZE
        robby.speed.right += STEP_SIZE
    if key_event[pygame.K_g]:
        robby.speed.left -= STEP_SIZE
        robby.speed.right -= STEP_SIZE
    if key_event[pygame.K_x]:
        robby.speed.left = 0
        robby.speed.right = 0
    if key_event[pygame.K_ESCAPE]:
        running = False
    robby._update_position()
    robby._draw(box.lines() + [line])
    box.draw(screen)

    pygame.draw.line(screen, (0, 0, 0), *line.to_tuple())
    pygame.display.update()
