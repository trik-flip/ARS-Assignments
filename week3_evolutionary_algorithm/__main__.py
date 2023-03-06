from .src.benchmarks import rastrigin, rosenbrock
from .src.simple.evolutionary_algorithm import EvolutionaryAlgorithm, sigmoid
from .src.robby.robot import Robot
import pygame


import pygame
from .src.robby.box import Box
from .src.robby.line import Line
from .src.robby.robot import Robot

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
robbies = [Robot(screen, direction=0) for _ in ea.population]
for r in robbies:
    r.set_position(240, 240)
    r.draw(box.lines() + [line1, line2, line3])

while running:
    screen.fill(background)
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            running = False
    for i, e in enumerate(ea.population):
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

        box.draw(screen)
        robbies[i].update_position(game_map)
        robbies[i].draw(game_map)

    pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
    pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
    pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
    pygame.display.update()

# pygame.init()
# (width, height) = (1900, 1060)
# WHITE = (255, 255, 255)
# background = WHITE

# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Robby Sim")
# screen.fill(background)

# robby = Robot(screen, direction=0)

# ea = EvolutionaryAlgorithm(population_size=20, input=0, hidden=[20, 20, 30], output=2)

# best = float("inf")
# unchanged = 0
# epoch = 0

# benchmark = rosenbrock

# while unchanged < 10:
#     epoch += 1
#     unchanged += 1

#     ea.epoch((), benchmark)

#     (org,) = ea.best()
#     result = org.run()
#     print(f"Current [{epoch:3}] - {result}, {benchmark(*result)}")

#     result = ea.best_organism.run()
#     print(f"Global  [{epoch:3}] - {result}, {benchmark(*result)}")
#     print()

#     ea.selection()
#     ea.repopulation()

#     if best > benchmark(*result):
#         unchanged = 0
#         best = benchmark(*result)
# res = ea.best_organism.run()
# print(res, ea.best_fitness)
# print(res, benchmark(*res))
