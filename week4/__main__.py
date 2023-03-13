import random
import pickle
import pygame
from time import time
from src.robby.box import Box
from src.robby.line import Line
from src.robby.robot import Robot
from src.simple.evolutionary_algorithm import EvolutionaryAlgorithm
from math import exp
from fitness import fitness
from src.benchmarks.rastrigin import rastrigin

def sigmoid(x):
    if x < -100:
        return 1
    elif x > 100:
        return -1
    return (1 / (1 + exp(-x)))*2 - 1

random.seed(42)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

STEP_SIZE = .01

benchmark = rastrigin
if benchmark == rastrigin:
    min_x, max_x = -5.12, 5.12
    min_y, max_y = -5.12, 5.12
elif benchmark == rosenbrock:
    min_x, max_x = -1.8, 1.8
    min_y, max_y = -1, 3

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

box = Box(200, 200, 1700, 880)
box.draw(screen)

game_map = box.lines() + [line1, line2, line3]

pygame.display.update()
# with open(f"ea.obj", "rb") as f:
#     ea = pickle.load(f)

ea = EvolutionaryAlgorithm(population_size=50, input=12,hidden=[10,6], output=2)
robbies = [Robot(screen, direction=0) for _ in ea.population]

best = float("inf")
unchanged = 0
epoch = 0
def game_loop(running,ea,robbies,timer:int):
    for r in robbies:
        r.set_position(240, 240)
        r.draw(box.lines() + [line1, line2, line3])
    frame_count = 0
    while running:
        frame_count += 1
        if frame_count  > timer:
            running = False
        screen.fill(background)
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

            box.draw(screen)
            robbies[i].update_position(game_map)
            robbies[i].draw(game_map)
        pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
        pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
        pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
        pygame.display.update()
while unchanged < 5:

    # x_and_ys = [p.run() for p in ea.population]
    # particles = np.array([ele for ele in x_and_ys])
    # fitnesshistory.append(min([benchmark(x, y) for x, y in particles]))
    # scatter.set_offsets([ele for ele in x_and_ys])
    # scatter.set_3d_properties([benchmark(x, y) for x, y in x_and_ys], "z")
    # points.set_data([x for x in range(epoch + 1)], fitnesshistory)
    # plt.draw()
    # plt.pause(0.01)

    # print(f"[{epoch}] - {ea.diversity():.3f}, {result}, {benchmark(*result):.6f}")

    collision_count = [0 for _ in ea.population]
    game_loop(running, ea.population, robbies, 1500)
    epoch += 1
    if best > ea.best_fitness:
        best = ea.best_fitness
        unchanged = 0
    else:
        unchanged += 1

    print(f"[{ea.generation_count}] - {ea.diversity():.3f}, {ea.best_fitness}")
    ea.epoch(robbies, fitness.fitfunc)
    ea.selection()
    ea.repopulate()
    robbies = [Robot(screen, direction=0) for _ in ea.population]
with open(f"ea-{ea.generation_count}.obj", "wb") as f:
    pickle.dump(ea, f)
    # (org,) = ea.best()
    # result = org.run(*[s.value for s in robbies[0].sensors])
print("trained")
game_loop(running, ea.population, robbies, 20000000)
