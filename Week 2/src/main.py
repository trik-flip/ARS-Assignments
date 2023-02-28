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


(width, height) = (1900, 1060)
STEP_SIZE = 0.1


box_x1 = 200
box_x2 = 1700
box_y1 = 200
box_y2 = 880

box_x21 = 200 + 150
box_x22 = 1700 - 150
box_y21 = 200 + 150
box_y22 = 880 - 150

background = WHITE
running = True
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

robby = Robot(screen, direction=0)
robby.set_position(240, 240)
box = Box(box_x1, box_y1, box_x2, box_y2)
box2 = Box(box_x21, box_y21, box_x22, box_y22)
box.draw(screen)
box2.draw(screen)
robby.draw(box.lines() + box2.lines())

pygame.display.update()
# line = Line(box_x1, box_y1, box_x2 / 2, box_y2 / 2)
# line2 = Line(box_x2 * 3 / 4, box_y2, box_x2, box_y1)

map = box.lines() + box2.lines()

pushed = [False in range(6)]
o_pushed = False
l_pushed = False
w_pushed = False
s_pushed = False
t_pushed = False
g_pushed = False

while running:
    screen.fill(background)
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Possible to use something like "last_pos = pygame.mouse.get_pos()"
            x, y = pygame.mouse.get_pos()
            robby.set_position(x, y)
        if event.type == pygame.QUIT:
            running = False

    key_event = pygame.key.get_pressed()

    if key_event[pygame.K_o] and o_pushed == False:
        robby.speed.right += STEP_SIZE
    o_pushed = key_event[pygame.K_o]

    if key_event[pygame.K_l] and l_pushed == False:
        robby.speed.right -= STEP_SIZE

    l_pushed = key_event[pygame.K_l]
    if key_event[pygame.K_w] and w_pushed == False:
        robby.speed.left += STEP_SIZE

    w_pushed = key_event[pygame.K_w]
    if key_event[pygame.K_s] and s_pushed == False:
        robby.speed.left -= STEP_SIZE

    s_pushed = key_event[pygame.K_s]
    if key_event[pygame.K_t] and t_pushed == False:
        robby.speed.left += STEP_SIZE
        robby.speed.right += STEP_SIZE

    t_pushed = key_event[pygame.K_t]
    if key_event[pygame.K_g] and g_pushed == False:
        robby.speed.left -= STEP_SIZE
        robby.speed.right -= STEP_SIZE

    g_pushed = key_event[pygame.K_g]

    if key_event[pygame.K_r]:
        robby.position.x = 240
        robby.position.y = 240
        robby.speed.left = 0
        robby.speed.right = 0
        robby.direction = 0

    if key_event[pygame.K_x]:
        robby.speed.left = 0
        robby.speed.right = 0

    if key_event[pygame.K_ESCAPE]:
        running = False

    robby.update_position(map)
    robby.draw(map)
    box.draw(screen)
    box2.draw(screen)

    # pygame.draw.line(screen, (0, 0, 0), *line.to_tuple())
    # pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
    pygame.display.update()
