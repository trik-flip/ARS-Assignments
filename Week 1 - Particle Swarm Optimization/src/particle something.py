import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource

N = 200
np.random.seed(420)
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

# min_x = -5.12
# max_x = 5.12
# min_y = -5.12
# max_y = 5.12
# benchmark = benchmark_rastrigin
#
min_x = -1.8
max_x = 1.8
min_y = -1
max_y = 3
benchmark = benchmark_rosenbrock

# weights for velocity

aa=0.9
bb=0.8
cc=0.8

# x = np.linspace(-1.8, 1.8, N)
# y = np.linspace(-1, 3, N)
# x, y = np.meshgrid(x, y)
# z = benchmark_rosenbrock(x, y)
#
# fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
# ls = LightSource(270, 45)
# surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=True)
# ax.set_title("rosenbrock")
# #plt.show()
#
#
# x = np.linspace(-5, 5, N)
# y = np.linspace(-5, 5, N)
# x, y = np.meshgrid(x, y)
# z = benchmark_rastrigin(x, y)
#
# fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
# ls = LightSource(270, 45)
# surf = ax.plot_surface(x, y, z, cmap=cm.jet, linewidth=0, antialiased=True)
# ax.set_title("rastrigin")
# #plt.show()

# creating a swarm

swarm_count=20
swarm_pos = np.random.rand(swarm_count, 2) * [max_x - min_x, max_y - min_y] + [min_x, min_y]
#print(swarm_pos)
score_pos=[[benchmark(swarm_pos[i][0],swarm_pos[i][1]),swarm_pos[i][0],swarm_pos[i][1]]for i in range(swarm_count)]
score_pos=np.array(score_pos)
#print(f"score and pos:{score_pos}")
global_pos = score_pos[np.argmin(score_pos[:,0])]
#print(f"global pos:{global_pos}")
#global_score= score.min()
#print(global_pos)
#print(global_score)
# velocity in two dimensions x and y random init
veloc = np.random.rand(swarm_count, 2)

x = np.linspace(min_x, max_x, N)
y = np.linspace(min_y, max_y, N)
x, y = np.meshgrid(x, y)
z = benchmark(x, y)

fig = plt.figure()
ax = plt.axes(projection='3d')

ax.plot_surface(x, y, z, cmap='hsv',antialiased=True,edgecolor='none',alpha=0.6)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z');

particle_history = [swarm_pos]
scatter = ax.scatter(
    swarm_pos[:, 0],
    swarm_pos[:, 1],
    [benchmark(x, y) for x, y in swarm_pos],
    c=[benchmark(x, y) for x, y in swarm_pos],
    linewidths=1,
    label="scatter",alpha=1
)
epoch = 1
# while ((round(abs(np.mean(swarm_pos[:,0])),2)>0 and round(abs(np.mean(swarm_pos[:,1])),2)>0)):
vel=np.array([math.sqrt(x**2+y**2) for x,y in veloc])

while np.mean(vel) > 1e-2:
# for i in range(20):  #epoch count
   # for i in range(swarm_count): # for each particle update velocity
    ax.set_title(f"Particle Swarm Optimization - epoch:{epoch}")
    R = np.random.uniform(0, 1)
    veloc = aa*veloc+(bb*R*(score_pos[:,1:]-swarm_pos))+(cc*R*(global_pos[1:]-swarm_pos))
    vel=np.array([math.sqrt(x**2+y**2) for x,y in veloc])
    swarm_pos=swarm_pos+veloc
    new_scores=np.array([benchmark(*p) for p in swarm_pos])
    for i in range(swarm_count):
        if(new_scores[i]<score_pos[i][0]):
            if(new_scores[i]<global_pos[0]):
                global_pos = [new_scores[i],swarm_pos[i][0],swarm_pos[i][1]]
            score_pos[i]=[new_scores[i],swarm_pos[i][0],swarm_pos[i][1]]
    particle_history.append(swarm_pos)
    scatter.set_offsets([[_x, _y] for _x, _y in swarm_pos])
    scatter.set_3d_properties([benchmark(x, y) for x, y in swarm_pos], "z")
    epoch+=1
    aa=aa/1.01
    plt.draw()
    plt.pause(0.1)
    #print(np.mean(vel))
plt.show()
print(global_pos)
print(f"score and pos:{score_pos}")


