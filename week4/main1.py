import pygame
from src.robby.box import Box
from src.robby.line import Line
from src.robby.robot import Robot
from src.simple.evolutionary_algorithm import EvolutionaryAlgorithm


def main():
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

    STEP_SIZE = 0.01

    (width, height) = (1900, 1060)

    point1 = 350, 350
    point2 = 350, 880 - 150
    point3 = 1700 - 150, 880 - 150

    line1 = Line(350, 351, *point2)
    line2 = Line(351, 880 - 150, *point3)
    line3 = Line(*point1, *point3)

    background = WHITE
    running = True
    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Robby Sim")
    screen.fill(background)

    box = Box(200, 200, 1700, 880)
    box.draw(screen)

    game_map = box.lines() + [line1, line2, line3]

    pygame.display.update()
    ea = EvolutionaryAlgorithm(population_size=20, input=12, output=2)
    robby = Robot(screen, direction=0)

    robby.set_position(240, 240)
    robby.draw(box.lines() + [line1, line2, line3])

    o_pushed = False
    l_pushed = False
    w_pushed = False
    s_pushed = False
    t_pushed = False
    g_pushed = False
    while running:
        screen.fill(background)
        robby.update_position(game_map)
        robby.draw(game_map)

        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                running = False
        key_event = pygame.key.get_pressed()

        if key_event[pygame.K_o]:
            robby.speed.right += STEP_SIZE * 0.1
        o_pushed = key_event[pygame.K_o]

        if key_event[pygame.K_l]:
            robby.speed.right -= STEP_SIZE * 0.1

        l_pushed = key_event[pygame.K_l]
        if key_event[pygame.K_w]:
            robby.speed.left += STEP_SIZE * 0.1

        w_pushed = key_event[pygame.K_w]
        if key_event[pygame.K_s]:
            robby.speed.left -= STEP_SIZE * 0.1

        s_pushed = key_event[pygame.K_s]
        if key_event[pygame.K_t]:
            robby.speed.left += STEP_SIZE
            robby.speed.right += STEP_SIZE

        t_pushed = key_event[pygame.K_t]
        if key_event[pygame.K_g]:
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

        pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
        pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
        pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
        pygame.display.update()
