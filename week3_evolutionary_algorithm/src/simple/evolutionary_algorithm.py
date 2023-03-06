from math import exp
from random import sample

from .evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism


def sigmoid(x):
    ex = exp(x)
    return ex / (ex + 1)


class EvolutionaryAlgorithm:
    new_population: list[EvolutionaryAlgorithmOrganism]
    population: list[EvolutionaryAlgorithmOrganism]
    fitness: list[float]
    population_size: int
    survival_rate: float
    best_organism: EvolutionaryAlgorithmOrganism
    best_fitness: float
    org_fit_list: list[tuple[EvolutionaryAlgorithmOrganism, float]]

    def __init__(
        self,
        population_size,
        survival_rate=0.2,
        *,
        input: int,
        hidden: list[int] = [],
        output: int,
    ) -> None:
        self.population_size = population_size
        self.survival_rate = survival_rate
        self.population = [
            EvolutionaryAlgorithmOrganism(input=input, hidden=hidden, output=output)
            for _ in range(population_size)
        ]
        self.best_organism = self.population[0]
        self.best_fitness = float("inf")
        self.not_in_timer = 0

    def epoch(self, input, bench):
        self.org_fit_list = [(ea, bench(*ea.run(*input))) for ea in self.population]
        self.fitness = self.__calc_fitness(input, bench)
        self.__update_global_best()

    def __calc_fitness(self, input, bench):
        return [bench(*ea.run(*input)) for ea in self.population]

    def repopulation(self):
        self.__breed()
        self.__mutate()
        self.population += self.new_population
        if self.not_in_timer > 5 and self.best_organism not in self.population:
            print("adding")
            self.__add_best_again()
        self.not_in_timer += self.best_organism not in self.population

    def __add_best_again(self, x=1):
        self.population[-x:] = [self.best_organism.copy() for _ in range(x)]

    def __mutate(self):
        for p in self.population:
            p.mutate()

    def __breed(self):
        self.new_population = []
        while len(self.new_population) < (self.population_size - len(self.population)):
            x, y = sample(self.population, 2)
            b = x.cross(y)
            self.new_population.append(b)

    def best(self, x=1):
        sorted_best = self.__sorted_population_fitness_list()[:x]
        return [ea for ea, _ in sorted_best]

    def __update_global_best(self):
        ea, fitness = sorted(self.org_fit_list, key=lambda x: x[1])[0]
        if fitness < self.best_fitness:
            self.best_organism = ea.copy()
            self.best_fitness = fitness

    def selection(self):
        self.population = self.best(int(self.population_size * self.survival_rate))

    def __population_fitness_list(self):
        return list(zip(self.population, self.fitness))

    def __sorted_population_fitness_list(self):
        return sorted(self.__population_fitness_list(), key=lambda x: x[1])
