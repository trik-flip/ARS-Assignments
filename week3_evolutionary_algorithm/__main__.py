import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib import cm
from matplotlib.colors import LightSource

from .src.benchmarks import rastrigin, rosenbrock
from .src.robby.box import Box
from .src.robby.line import Line
from .src.robby.robot import Robot
from .src.simple.evolutionary_algorithm import EvolutionaryAlgorithm, sigmoid

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

STEP_SIZE = 0.1


# (width, height) = (1900, 1060)


# point1 = 350, 350
# point2 = 350, 880 - 150
# point3 = 1700 - 150, 880 - 150

# line1 = Line(350, 351, *point2)
# line2 = Line(351, 880 - 150, *point3)
# line3 = Line(*point1, *point3)

# background = WHITE
# running = True
# pygame.init()

# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Robby Sim")
# screen.fill(background)

# box = Box(200, 200, 1700, 880)
# box.draw(screen)

# game_map = box.lines() + [line1, line2, line3]

# pygame.display.update()
# ea = EvolutionaryAlgorithm(population_size=20, input=12, output=2)
# robbies = [Robot(screen, direction=0) for _ in ea.population]
# for r in robbies:
#     r.set_position(240, 240)
#     r.draw(box.lines() + [line1, line2, line3])

# while running:
#     screen.fill(background)
#     ev = pygame.event.get()
#     for event in ev:
#         if event.type == pygame.QUIT:
#             running = False
#     for i, e in enumerate(ea.population):
#         result = e.run(*[s.value for s in robbies[i].sensors])
#         result = list(map(sigmoid, result))
#         if result[0] > 0.5:
#             robbies[i].speed.right += STEP_SIZE
#         elif result[0] < -0.5:
#             robbies[i].speed.right -= STEP_SIZE

#         if result[1] > 0.5:
#             robbies[i].speed.left += STEP_SIZE
#         elif result[1] < -0.5:
#             robbies[i].speed.left -= STEP_SIZE

#         key_event = pygame.key.get_pressed()
#         if key_event[pygame.K_r]:
#             robbies[i].position.x = 240
#             robbies[i].position.y = 240
#             robbies[i].speed.left = 0
#             robbies[i].speed.right = 0
#             robbies[i].direction = 0

#         if key_event[pygame.K_ESCAPE]:
#             running = False

#         box.draw(screen)
#         robbies[i].update_position(game_map)
#         robbies[i].draw(game_map)

#     pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
#     pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
#     pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
#     pygame.display.update()

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


benchmark = rosenbrock


ea = EvolutionaryAlgorithm(population_size=20, input=0, output=2)
x_and_ys = [p.run() for p in ea.population]

# region benchmark plot
min_x, max_x = -1.8, 1.8
min_y, max_y = -1, 3
x = np.linspace(min_x, max_x, 300)
y = np.linspace(min_y, max_y, 300)
x, y = np.meshgrid(x, y)
z = benchmark(x, y)
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ls = LightSource(500, 90)
surf = ax1.plot_surface(
    x, y, z, cmap=cm.jet, edgecolor="black", linewidth=0.02, zorder=-1, alpha=0.1
)
# endregion

# region plot particles based on the EA initialisation
particles_x = [coord[0] for coord in x_and_ys]
particles_y = [coord[1] for coord in x_and_ys]
particles = np.array([ele for ele in x_and_ys])

scatter = ax1.scatter(
    particles_x,
    particles_y,
    [benchmark(x, y) for x, y in particles],
    c=[0 for _ in particles],
    linewidths=0,
    label="scatter",
)
# endregion


plt.draw()
plt.waitforbuttonpress()


best = float("inf")
unchanged = 0
epoch = 0


while unchanged < 100:
    epoch += 1
    ea.epoch((), benchmark)
    ea.selection()
    ea.repopulation()

    (org,) = ea.best()
    result = org.run()

    x_and_ys = [p.run() for p in ea.population]
    scatter.set_offsets([(x, y) for x, y in x_and_ys])
    scatter.set_3d_properties([benchmark(x, y) for x, y in x_and_ys], "z")
    plt.draw()
    plt.pause(0.1)

    print(epoch, result, benchmark(*result))
    if best > benchmark(*result):
        unchanged = 0
        best = benchmark(*result)
    else:
        unchanged += 1
plt.show()
