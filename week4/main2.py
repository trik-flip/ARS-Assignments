import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource
from src.benchmarks.rastrigin import rastrigin
from src.benchmarks.rosenbrock import rosenbrock
from src.simple.evolutionary_algorithm import EvolutionaryAlgorithm


def main():
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
        ea.repopulate()
        (org,) = ea.best()
        result = org.run()

        x_and_ys = [p.run() for p in ea.population]
        scatter.set_offsets([(x, y) for x, y in x_and_ys])
        scatter.set_3d_properties([benchmark(x, y) for x, y in x_and_ys], "z")
        plt.draw()
        plt.pause(0.1)

        print(f"[{epoch}] - {ea.diversity():.3f}, {result}, {benchmark(*result):.6f}")
        if best > benchmark(*result):
            unchanged = 0
            best = benchmark(*result)
        else:
            unchanged += 1
    plt.show()
