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
STEP_SIZE = 0.001


box_x1=200
box_x2=1700
box_y1=200
box_y2=880
box_tuple= (box_x1, box_y1, box_x2, box_y2)
background = WHITE
running = True
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

robby = Robot(screen, direction=pi)
box = Box(box_x1, box_y1, box_x2, box_y2)  # box
box.draw(screen)
robby._draw(box.lines())
pygame.display.update()
line = Line(0,0,0,0)
# line = Line(200, 500, 700, 200)
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
    if key_event[pygame.K_r]:
        robby.position.x=1920 / 2
        robby.position.y=1080 / 2
        robby.speed.left = 0
        robby.speed.right = 0
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
