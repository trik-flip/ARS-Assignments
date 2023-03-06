from typing import Callable
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

np.random.seed(42)


def speed_of(vel):
    return [(x**2 + y**2) ** (1 / 2) for x, y in vel]


def update(pos, vel, p_best, g_best, bench, a, b, c):
    rng = np.random.default_rng(12345)
    for i, p in enumerate(pos):
        score = bench(*p)
        if p_best[i][0] > score:
            if g_best[0] > score:
                g_best = score, *p
            p_best[i] = score, *p
    R = rng.random()

    vel = a * vel + b * R * (p_best[:, 1:] - pos) + c * R * (g_best[1:] - pos)

    new_pos = pos + vel
    return new_pos, vel, p_best, g_best


BenchmarkFunction = Callable[[float, float], float]


def benchmark_rosenbrock(x, y, a=1, b=100):
    """Min at (x=a, y=a**2)"""
    return (a - x) ** 2 + b * (y - x**2) ** 2


def _benchmark_rastrigin(x, n, A):
    """Min at x = 0"""
    points = np.linspace(-x, x, n)
    return A * n + sum([y**2 - A * np.cos(2 * np.pi * y) for y in points])


def benchmark_rastrigin(x, y, n=2, A=10):
    """Min at (x=0, y=0)"""
    return _benchmark_rastrigin(x, n, A) + _benchmark_rastrigin(y, n, A)


if __name__ == "__main__":
    N = 300
    # region benchmark function
    func = "rastrigin"
    if func == "rastrigin":
        min_x, max_x = -5.12, 5.12
        min_y, max_y = -5.12, 5.12
        benchmark = benchmark_rastrigin
    elif func == "rosenbrock":
        min_x, max_x = -1.8, 1.8
        min_y, max_y = -1, 3
        benchmark = benchmark_rosenbrock
    else:
        raise Exception("Unknown benchmark")
    # endregion

    number_of_particles = 30
    nx = int(np.sqrt(number_of_particles))
    ny = number_of_particles // nx

    # region initial Placement

    # region Systematic placement
    particles_x = np.linspace(min_x, max_x, nx)
    particles_y = np.linspace(min_y, max_y, ny)
    particles = np.array([[x, y] for x in particles_x for y in particles_y])
    # endregion

    # region Random placement
    # particles = np.random.rand(number_of_particles, 2) * [max_x - min_x, max_y - min_y] + [min_x, min_y]
    # endregion

    # endregion

    # region initial velocity
    ## random
    velocity = (np.random.rand(number_of_particles, 2) * 2) - 1
    # endregion

    # region initialize starting values
    epoch = 0
    score_x_y = [[benchmark(x, y), x, y] for x, y in particles]
    pbest = np.array(score_x_y)
    gbest = min(pbest, key=lambda x: x[0])

    x = np.linspace(min_x, max_x, N)
    y = np.linspace(min_y, max_y, N)
    x, y = np.meshgrid(x, y)
    z = benchmark(x, y)
    # endregion

    # region define plots
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(
        1,
        2,
        2,
    )

    ls = LightSource(270, 45)
    surf = ax1.plot_surface(  # type: ignore
        x, y, z, cmap=cm.jet, edgecolor="black", linewidth=0.02, zorder=-1, alpha=0.1  # type: ignore
    )
    particle_history = [particles]
    g_history = [gbest[0]]
    p_history = [pbest[:, 0]]
    scatter = ax1.scatter(
        particles[:, 0],
        particles[:, 1],
        [benchmark(x, y) for x, y in particles],
        c=[0 for _ in particles],
        linewidths=0,
        label="scatter",
    )
    # endregion

    # region draw the screen
    (points,) = ax2.plot([0], g_history)
    plt.draw()
    plt.waitforbuttonpress()
    plt.waitforbuttonpress()
    # endregion

    # region initialize parameter values
    a = 0.8
    b = 2
    c = 2
    # endregion

    while np.mean(speed_of(velocity)) > 1e-3:
        epoch += 1
        # region update plot view
        ax1.set_title(f"with particles - epoch:{epoch}")
        ax2.set_xlim(0, epoch + 2)
        ax2.set_ylim(0, max(g_history) * 1.1)
        # endregion

        # region update plot data
        particles, velocity, pbest, gbest = update(
            particles, velocity, pbest, gbest, benchmark, max(0.4, a), b, c
        )
        # endregion

        # region update weights in variable
        a /= 1.1
        b /= 1
        c /= 1
        # endregion

        # region record history
        particle_history.append(particles)
        g_history.append(gbest[0])
        p_history.append(pbest[:, 0])
        # endregion

        # region Update plot with new data
        scatter.set_offsets([[_x, _y] for _x, _y in particles])
        scatter.set_3d_properties([benchmark(x, y) for x, y in particles], "z")  # type: ignore
        points.set_data([x for x in range(epoch + 1)], g_history)
        # endregion

        plt.draw()
        plt.pause(0.01)

    plt.show()
    print(particles)
    print(gbest[0])
