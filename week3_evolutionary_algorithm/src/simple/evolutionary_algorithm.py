import numpy as np
from math import exp
from random import sample


def sigmoid(x):
    ex = exp(x)
    return ex / (ex + 1)


class EvolutionaryAlgorithmOrganism:
    def __init__(self, *, input: int, hidden: list[int] = [], output: int) -> None:
        assert output is not None
        self.input = np.zeros(input + 1)
        self.input[-1] = 1
        self.hidden = [np.zeros(n + 1) for n in hidden]
        for l in self.hidden:
            l[-1] = 1
        self.output = np.zeros(output)

        self.network = [self.input, *self.hidden, self.output]
        self.weights = []

        for i, layer in enumerate(self.network[:-1]):
            self.weights.append(np.random.rand(len(layer), len(self.network[i + 1])))

    def run(self, *input_data):
        assert len(input_data) == len(self.input) - 1
        for i, val in enumerate(input_data):
            self.input[i] = val
        self.input[-1] = 1
        for i, layer in enumerate(self.network[:-1]):
            self.network[i + 1] = layer.dot(self.weights[i])
        self.output = self.network[-1]
        return self.output

    def cross(self, ea2):
        assert isinstance(ea2, EvolutionaryAlgorithmOrganism)
        baby = EvolutionaryAlgorithmOrganism(
            input=len(self.input) - 1, output=len(self.output)
        )
        for i, w in enumerate(baby.weights):
            if np.random.random() > 0.5:
                new_weight = self.weights[i]
            else:
                new_weight = ea2.weights[i]

            for j, _w in enumerate(new_weight):
                baby.weights[i][j] = _w

        return baby

    def mutate(self):
        for i, w in enumerate(self.weights):
            for j, n in enumerate(w):
                self.weights[i][j] = self.weights[i][j] + np.random.random() - 0.5


class EvolutionaryAlgorithm:
    new_population: list[EvolutionaryAlgorithmOrganism]
    population: list[EvolutionaryAlgorithmOrganism]
    fitness: list[float]
    population_size: int

    def __init__(
        self, population_size, *, input: int, hidden: list[int] = [], output: int
    ) -> None:
        self.population_size = population_size
        self.population = [
            EvolutionaryAlgorithmOrganism(input=input, hidden=hidden, output=output)
            for _ in range(population_size)
        ]

    def epoch(self, input, bench):
        self.fitness = []
        for ea in self.population:
            z = ea.run(*input)
            distance = bench(*z)
            self.fitness.append(distance)

    def repopulation(self):
        self._breed()
        self._mutate()
        self.population += self.new_population

    def _mutate(self):
        for p in self.population:
            p.mutate()

    def _breed(self):
        self.new_population = []
        while len(self.new_population) < (self.population_size - len(self.population)):
            x, y = sample(self.population, 2)
            b = x.cross(y)
            self.new_population.append(b)

    def best(self, x=1):
        samples_and_fitness = zip(self.population, self.fitness)
        return [
            ea
            for ea, _ in sorted(
                samples_and_fitness,
                key=lambda x: x[1],
            )[:x]
        ]

    def selection(self, survival_rate=0.2):
        samples_and_fitness = [(x, y) for x, y in zip(self.population, self.fitness)]
        best_samples = sorted(
            samples_and_fitness,
            key=lambda x: x[1],
        )[: int(self.population_size * survival_rate)]

        self.population = [ea for ea, _ in best_samples]


pop = [EvolutionaryAlgorithmOrganism(input=2, output=1) for _ in range(20)]
input = 3, 5
output = sum(input)
