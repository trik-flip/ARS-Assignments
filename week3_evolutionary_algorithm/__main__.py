import numpy as np

from .src.benchmarks import rastrigin, rosenbrock
from .src.simple.evolutionary_algorithm import EvolutionaryAlgorithm

ea = EvolutionaryAlgorithm(population_size=20, input=0, output=2)
best = float("inf")
unchanged = 0
epoch = 0
while unchanged < 100:
    epoch += 1
    ea.epoch((), rosenbrock)
    ea.selection()
    ea.repopulation()

    (org,) = ea.best()
    result = org.run()
    print(epoch, result, rosenbrock(*result))
    if best > rosenbrock(*result):
        unchanged = 0
        best = rosenbrock(*result)
    else:
        unchanged += 1
