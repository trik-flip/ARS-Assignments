import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

np.random.seed(42)

N = 300


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


def benchmark_rosenbrock(x, y, a=1, b=100):
    # Min at (x=a, y=a**2)
    return (a - x) ** 2 + b * (y - x**2) ** 2


def _benchmark_rastrigin(x, n, A):
    # Min at x = 0
    points = np.linspace(-x, x, n)
    return A * n + sum([y**2 - A * np.cos(2 * np.pi * y) for y in points])


def benchmark_rastrigin(x, y, n=2, A=10):
    # Min at (x=0, y=0)
    return _benchmark_rastrigin(x, n, A) + _benchmark_rastrigin(y, n, A)


# min_x = -5.12
# max_x = 5.12
# min_y = -5.12
# max_y = 5.12
# benchmark = benchmark_rastrigin

min_x = -1.8
max_x = 1.8
min_y = -1
max_y = 3
benchmark = benchmark_rosenbrock

number_of_particles = 30
nx = int(np.sqrt(number_of_particles))
ny = number_of_particles // nx

# Placement
## Systematic placement
particles_x = np.linspace(min_x, max_x, nx)
particles_y = np.linspace(min_y, max_y, ny)
particles = np.array([[x, y] for x in particles_x for y in particles_y])

## Random placement
# particles = np.random.rand(number_of_particles, 2) * [max_x - min_x, max_y - min_y] + [min_x, min_y]

## Random init
velocity = np.random.rand(number_of_particles, 2)

score_x_y = [[benchmark(x, y), x, y] for x, y in particles]
pbest = np.array(score_x_y)
gbest = min(pbest, key=lambda x: x[0])
print(pbest)
print(gbest)


x = np.linspace(min_x, max_x, N)
y = np.linspace(min_y, max_y, N)
x, y = np.meshgrid(x, y)
z = benchmark(x, y)

# fig, ax1 = plt.subplots(subplot_kw=dict(projection="3d"))
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
ax2 = fig.add_subplot(
    1,
    2,
    2,
)
# ax3 = fig.add_subplot(
#     1,
#     3,
#     3,
# )

ls = LightSource(270, 45)
surf = ax1.plot_surface(
    x, y, z, cmap=cm.jet, edgecolor="black", linewidth=0.02, zorder=-1, alpha=0.1
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
plt.draw()
plt.waitforbuttonpress()
plt.waitforbuttonpress()

epoch = 0
a = 0.8
b = 1.2
c = 0.8
(points,) = ax2.plot([epoch], g_history)


def speed_of(vel):
    return [(x**2 + y**2) ** (1 / 2) for x, y in vel]


while np.mean(speed_of(velocity)) > 1e-3:
    # while velocity.max() > 1e-3:
    epoch += 1
    ax1.set_title(f"with particles - epoch:{epoch}")
    ax2.set_xlim(0, epoch + 2)
    # ax2.set_ylim(0, max(g_history[len(g_history)//4 :]) * 1.1)
    ax2.set_ylim(0, max(g_history) * 1.1)

    particles, velocity, pbest, gbest = update(
        particles, velocity, pbest, gbest, benchmark, max(0.4, a), b, c
    )
    a /= 1.1
    # b /= 1.1
    # c /= 1.1

    particle_history.append(particles)
    scatter.set_offsets([[_x, _y] for _x, _y in particles])
    scatter.set_3d_properties([benchmark(x, y) for x, y in particles], "z")

    g_history.append(gbest[0])
    p_history.append(pbest[:, 0])
    points.set_data([x for x in range(epoch + 1)], g_history)
    # points2.set_data([[x for x in range(epoch + 1)] for _ in p_history[0]], p_history)
    plt.draw()
    plt.pause(0.01)
plt.show()
print(particles)
print(gbest)
