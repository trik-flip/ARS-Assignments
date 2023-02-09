import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

np.random.seed(42)

N = 300


def update(pos, vel, pbest, gbest, bench, a, b, c):
    new_pos = pos + vel
    rng = np.random.default_rng(12345)
    scores = np.array([bench(*p) for p in pos])
    for i, p in enumerate(pos):
        score = bench(*p)
        if pbest[i][0] > score:
            if gbest[0] > score:
                gbest = score, *p
            pbest[i] = score, *p
    R = rng.random()

    vel = a * vel + b * R * (pbest[:, 1:] - pos) + c * R * (gbest[1:] - pos)

    return new_pos, vel, pbest, gbest


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


x = np.linspace(-1.8, 1.8, N)
y = np.linspace(-1, 3, N)
x, y = np.meshgrid(x, y)
z = benchmark_rosenbrock(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=False)
ax.set_title("rosenbrock")
plt.show()


x = np.linspace(-5, 5, N)
y = np.linspace(-5, 5, N)
x, y = np.meshgrid(x, y)
z = benchmark_rastrigin(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=False)
ax.set_title("rastrigin")
plt.show()


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
number_of_particles = 20
nx = int(np.sqrt(number_of_particles))
ny = number_of_particles // nx

# Systematic placement
particles_x = np.linspace(min_x, max_x, nx)
particles_y = np.linspace(min_y, max_y, ny)
particles = np.array([[x, y] for x in particles_x for y in particles_y])

## Random placement
# particles = np.random.rand(20, 2) * [max_x - min_x, max_y - min_y] + [min_x, min_y]

## Random init
velocity = np.random.rand(20, 2)
score_x_y = [[benchmark(x, y), x, y] for x, y in particles]
pbest = np.array(score_x_y)
gbest = min(pbest, key=lambda x: x[0])
print(pbest)
print(gbest)


x = np.linspace(min_x, max_x, N)
y = np.linspace(min_y, max_y, N)
x, y = np.meshgrid(x, y)
z = benchmark(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
particle_history = [particles]
for i in range(200):
    particles, velocity, pbest, gbest = update(
        particles, velocity, pbest, gbest, benchmark, 0.3, 0.8, 0.8
    )
    particle_history.append(particles)
    print(particles[0])
ax.scatter(
    particles[:, 0],
    particles[:, 1],
    [benchmark(x, y) for x, y in particles],
    c=[0 for x, y in particles],
    linewidths=10,
)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=False)
ax.set_title("rastrigin with particles")
plt.show()
print(particle_history)
print(gbest)
