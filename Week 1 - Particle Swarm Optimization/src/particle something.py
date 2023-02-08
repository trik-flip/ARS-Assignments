import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

N = 20


def benchmark_rosenbrock(x, y, a=1, b=100):
    # Min at (x=a, y=a**2)
    return (a - x) ** 2 + b * (y - x**2) ** 2


def _benchmark_rastrigin(x, n, A):
    # Min at x = 0
    points = np.linspace(-x, x, n)
    return A * n + sum([y**2 - A * np.cos(2 * np.pi * y) for y in points])


def benchmark_rastrigin(x, y, n=2, A=10):
    return (x ** 2 - 10 * np.cos(2 * np.pi * x)) + (y ** 2 - 10 * np.cos(2 * np.pi * y)) + 10*n
    # Min at (x=0, y=0)
    #return _benchmark_rastrigin(x, n, A) + _benchmark_rastrigin(y, n, A)

x = np.linspace(-5, 5, N)
y = np.linspace(-5, 5, N)
x, y = np.meshgrid(x, y)
z = benchmark_rosenbrock(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=True)
plt.show()


x = np.linspace(-5.0, 5.0, N)
y = np.linspace(-5.0, 5.0, N)
x, y = np.meshgrid(x, y)
z = benchmark_rastrigin(x, y)

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
ls = LightSource(270, 45)
surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=True)
plt.show()


# trying to create a swarm

swarm_count=20
swarm_pos = np.zeros((swarm_count, 2)) #array for swarm
for i in range(swarm_count):
  x = np.random.uniform(-5, 5)
  y = np.random.uniform(-5, 5)
  swarm_pos[i][0] = x
  swarm_pos[i][1] = y
local_best_pos=swarm_pos # at step 0
print(local_best_pos)
score=np.zeros(swarm_count)
for i in range(swarm_count):
    score[i]=benchmark_rosenbrock(swarm_pos[i][0],swarm_pos[i][1])
print(score)
global_pos = local_best_pos[score.argmin(), :]
global_score= score.min()
print(global_pos)
print(global_score)
# velocity in two dimensions x and y
veloc=np.zeros((swarm_count, 2))
R=np.random.uniform(0,1,size=(swarm_count,2))
aa=0.9
bb=2
cc=2
for i in range(100): # for some time t say 100
   # for i in range(swarm_count): # for each particle update velocity
    veloc= (aa*veloc)+(bb*R*(local_best_pos-swarm_pos))+(cc*R*(global_pos-swarm_pos))
    swarm_pos=swarm_pos=veloc
for i in range(swarm_count):
    score[i] = benchmark_rosenbrock(swarm_pos[i][0], swarm_pos[i][1])
print(score[0])