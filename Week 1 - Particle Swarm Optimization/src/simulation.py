import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

N = 300


def benchmark_rosenbrock(x, y, a=1, b=100):
    # Min at (x=a, y=a**2)
    return (a - x) ** 2 + b * (y - x**2) ** 2


def _benchmark_rastrigin(x, n, A):
    # Min at x = 0
    points = np.linspace(-x, x, n)
    return A * n + sum([y**2 - A * np.cos(2 * np.pi * y) for y in points])


def benchmark_rastrigin(x, y, n=1, A=10):
    # Min at (x=0, y=0)
    return _benchmark_rastrigin(x, n, A) + _benchmark_rastrigin(y, n, A)


x = np.linspace(-1.8, 1.8, N)
y = np.linspace(-1, 3, N)
x, y = np.meshgrid(x, y)
z = benchmark_rosenbrock(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=False)
plt.show()


x = np.linspace(-5, 5, N)
y = np.linspace(-5, 5, N)
x, y = np.meshgrid(x, y)
z = benchmark_rastrigin(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=False)
plt.show()
