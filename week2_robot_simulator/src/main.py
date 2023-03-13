import pygame
from box import Box
from line import Line
from robot import Robot

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

STEP_SIZE = 0.1


(width, height) = (1900, 1060)


point1 = 350, 350
point2 = 350, 880 - 150
point3 = 1700 - 150, 880 - 150

line1 = Line(350, 350, *point2)
line2 = Line(350, 880 - 150, *point3)
line3 = Line(*point1, *point3)

background = WHITE
running = True
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

robby = Robot(screen, direction=0)
robby.set_position(240, 240)
box = Box(200, 200, 1700, 880)
box.draw(screen)

robby.draw(box.lines() + [line1, line2, line3])
map = box.lines() + [line1, line2, line3]

pygame.display.update()

dt = 0
dt_last = 0

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

    box.draw(screen)
    robby.update_position(map)
    robby.draw(map)

    pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
    pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
    pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
    pygame.display.update()
