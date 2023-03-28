from math import atan2
import pygame
from src.simulator.robot import Robot
from src.simulator.position import Position
from src.simulator.pose import Pose
from itertools import combinations

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
LIGHT_BLUE = (80, 180, 255)
STEP_SIZE = 0.1

robby = Robot(position=(240, 240), direction=0)
beacons = [
    Position(400, 400),
    Position(500, 450),
    Position(500, 350),
    Position(1500, 450),
    Position(1500, 350),

]

pygame.init()
pygame.display.set_caption("Robby Sim")
screen = pygame.display.set_mode((1920, 1080))


def draw_beacon(screen, robby: Robot, p: Position):
    pygame.draw.circle(
        screen,
        BLACK,
        p.xy,
        5,
    )
    if (d := robby.pose.position.d(p)) < 200:
        cr, cg, cb = LIGHT_BLUE

        cr += (d / 200) * (255 - 80)
        cg -= (d / 200) * cg
        cb -= (d / 200) * cb

        pygame.draw.line(screen, (cr, cg, cb), p.xy, robby.pose.position.xy, 3)
        pygame.draw.circle(screen, BLACK, p.xy, d, 1)

        a = atan2(p.dy(robby.pose.position), p.dx(robby.pose.position))

        # print(a / pi * 180)


running = True


def draw_intersection(color, screen, p):
    if p is None:
        return

    assert isinstance(p, tuple)
    bp1, bp2 = p

    assert isinstance(bp1, Position)
    assert isinstance(bp2, Position)

    pygame.draw.circle(screen, color, bp1.xy, 5, 1)
    pygame.draw.circle(screen, color, bp2.xy, 5, 1)


while running:
    screen.fill(WHITE)
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            robby.pose.position = x, y
        if event.type == pygame.QUIT:
            running = False

    key_event = pygame.key.get_pressed()

    if key_event[pygame.K_w]:
        robby.speed += STEP_SIZE / 10

    if key_event[pygame.K_s]:
        robby.speed -= STEP_SIZE / 10

    if key_event[pygame.K_a]:
        robby.steering_angle -= STEP_SIZE / 10

    if key_event[pygame.K_d]:
        robby.steering_angle += STEP_SIZE / 10

    if key_event[pygame.K_r]:
        robby.mu = Pose(Position.place_with_noise(240, 240, k=10)).array
        robby.pose.position = 240, 240
        robby.speed = 0
        robby.pose._direction = 0

    if key_event[pygame.K_x]:
        robby.speed = 0

    if key_event[pygame.K_ESCAPE]:
        running = False

    robby.update(beacons)
    robby.draw(screen)

    for _b1, _b2, _b3 in combinations(beacons, 3):
        bp = robby.pose.position.triangulate_with_beacons(_b1, _b2, _b3)
        if bp is not None:
            pygame.draw.circle(screen, LIGHT_BLUE, bp.xy, 10, 2)

    for _b1, _b2 in combinations(beacons, 2):
        p = robby.pose.position.intersection_of_beacon(_b1, _b2)
        draw_intersection(RED, screen, p)

    for b in beacons:
        draw_beacon(screen, robby, b)

    pygame.display.update()
