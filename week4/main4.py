import random
import pickle
import pygame
from src.robby.box import Box
from src.robby.line import Line
from src.robby.robot import Robot
from src.simple.evolutionary_algorithm import EvolutionaryAlgorithm
from math import exp
from fitness import fitness


def sigmoid(x):
    if x < -100:
        return 1
    elif x > 100:
        return -1
    return (1 / (1 + exp(-x))) * 2 - 1


random.seed(42)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
STEP_SIZE = 0.01


def game_loop(running, ea, robbies, timer: int, screen, all_lines: list[Line]):
    for r in robbies:
        r.set_position(240, 240)
        r.draw(all_lines)
    frame_count = 0
    while running:
        frame_count += 1
        if frame_count > timer:
            running = False
        screen.fill(WHITE)
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                running = False
        for i, e in enumerate(ea):
            result = e.run(*[s.value for s in robbies[i].sensors])
            result = list(map(sigmoid, result))
            if result[0] > 0.5:
                robbies[i].speed.right += STEP_SIZE
            elif result[0] < -0.5:
                robbies[i].speed.right -= STEP_SIZE

            if result[1] > 0.5:
                robbies[i].speed.left += STEP_SIZE
            elif result[1] < -0.5:
                robbies[i].speed.left -= STEP_SIZE

            key_event = pygame.key.get_pressed()
            if key_event[pygame.K_r]:
                robbies[i].position.x = 240
                robbies[i].position.y = 240
                robbies[i].speed.left = 0
                robbies[i].speed.right = 0
                robbies[i].direction = 0

            if key_event[pygame.K_ESCAPE]:
                running = False

            robbies[i].update_position(all_lines)
            robbies[i].draw(all_lines)
        for line in all_lines:
            pygame.draw.line(screen, BLACK, *line.to_tuple())
        pygame.display.update()


def main(load_from_file=False):
    (width, height) = (1900, 1060)

    point1 = 350, 350
    point2 = 350, 880 - 150
    point3 = 1700 - 150, 880 - 150

    line1 = Line(350, 350, *point2)
    line2 = Line(350, 880 - 150, *point3)
    line3 = Line(*point1, *point3)

    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Robby Sim")

    box = Box(200, 200, 1700, 880)
    box.draw(screen)

    game_map = box.lines() + [line1, line2, line3]

    pygame.display.update()

    if load_from_file:
        with open(f"ea.obj", "rb") as f:
            ea = pickle.load(f)
    else:
        ea = EvolutionaryAlgorithm(
            population_size=50, input=12, hidden=[10, 6], output=2, recur=-2
        )

    robbies = [Robot(screen, direction=0) for _ in ea.population]

    while ea.no_better_counter < 5:
        game_loop(True, ea.population, robbies, 1500, screen, game_map)

        print(f"[{ea.generation_count}] - {ea.diversity():.3f}, {ea.best_fitness}")
        ea.epoch(robbies, fitness.fitfunc)
        ea.selection()
        ea.repopulate()
        robbies = [Robot(screen, direction=0) for _ in ea.population]
    with open(f"ea-{ea.generation_count}.obj", "wb") as f:
        pickle.dump(ea, f)
    print("trained")
    game_loop(True, ea.population, robbies, 20000000, screen, game_map)
