import random
from math import exp
from matplotlib import pyplot as plt
from numpy import average

import pygame
from fitness import fitness
from src.robby.box import Box
from src.robby.line import Line
from src.robby.robot import Robot
from src.simple.evolutionary_algorithm import EvolutionaryAlgorithm
from src.simple.evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism


def sigmoid(x):
    if x < -100:
        return 1.0
    elif x > 100:
        return -1.0
    return (1 / (1 + exp(-x))) * 2 - 1


random.seed(42)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
STEP_SIZE = 0.01


def game_loop(
    organisms: list[EvolutionaryAlgorithmOrganism],
    robots: list[Robot],
    timer: int,
    screen,
    all_lines: list[Line],
):
    for robot in robots:
        robot.set_position(240, 240)
        robot.draw(all_lines)
    for i in range(3):
        robots[i].draw_slime()
    for i in range(3):
        robots[i].draw(all_lines)

    frame_count: int = 0
    running: bool = True

    while running:
        frame_count += 1

        if frame_count > timer:
            running = False

        screen.fill(WHITE)
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                running = False

        for org, robot in zip(organisms, robots):
            result = org.run(*[s.value for s in robot.sensors])
            right, left = list(map(sigmoid, result))
            if right > 0.5:
                robot.speed.right += STEP_SIZE
            elif right < -0.5:
                robot.speed.right -= STEP_SIZE

            if left > 0.5:
                robot.speed.left += STEP_SIZE
            elif left < -0.5:
                robot.speed.left -= STEP_SIZE

            key_event = pygame.key.get_pressed()
            if key_event[pygame.K_r]:
                robot.position.x = 240
                robot.position.y = 240
                robot.speed.left = 0
                robot.speed.right = 0
                robot.direction = 0

            if key_event[pygame.K_ESCAPE]:
                running = False

            robot.update_position(all_lines)
        for i in range(3):
            robots[i].draw_slime()
        for i in range(3):
            robots[i].draw(all_lines)

        for line in all_lines:
            pygame.draw.line(screen, BLACK, *line.to_tuple())
        pygame.display.update()


def main(load_from_file=False):
    avg_fitness_over_time = []
    best_fitness_over_time = []
    diversity_over_time = []
    (width, height) = (1920, 1080)

    point1 = 350, 350
    point2 = 350, 880 - 150
    point3 = 1700 - 150, 880 - 150

    line1 = Line(*point1, *point2)
    line2 = Line(*point2, *point3)
    line3 = Line(*point1, *point3)

    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Robby Sim")

    box = Box(200, 200, 1700, 880)
    box.draw(screen)

    game_map = box.lines() + [line1, line2, line3]

    pygame.display.update()

    if load_from_file:
        ea = EvolutionaryAlgorithm.load("ea.obj")
    else:
        ea = EvolutionaryAlgorithm(
            survival_rate=0.5,
            population_size=12,
            input=12,
            hidden=[10, 6],
            output=2,
            recur=-2,
            mutation_rate=0.0,
        )

    robots = [Robot(screen, direction=0) for _ in ea.population]

    while ea.no_better_counter < 5:
        game_loop(ea.population, robots, 1500, screen, game_map)
        print(f"[{ea.generation_count}] - {ea.diversity():.3f}, {ea.best_fitness}")
        ea.epoch(robots, fitness.fitfunc)
        avg = average(ea.fitness)
        best = min(ea.fitness)

        avg_fitness_over_time.append(avg)
        best_fitness_over_time.append(best)
        diversity_over_time.append(ea.diversity())

        ea.selection()
        ea.repopulate()

        robots = [Robot(screen, direction=0) for _ in ea.population]
        if ea.generation_count % 5 == 0:
            ea.save(f"ea-{ea.generation_count}-intermediate.obj")
    plt.plot(avg_fitness_over_time)
    plt.title("avg_fitness_over_time")
    plt.show()
    plt.plot(best_fitness_over_time)
    plt.title("best_fitness_over_time")
    plt.show()
    plt.plot(diversity_over_time)
    plt.title("diversity_over_time")
    plt.show()

    ea.save(f"ea-{ea.generation_count}.obj")

    print("trained")
    game_loop(ea.sorted_population(), robots, 20000000, screen, game_map)