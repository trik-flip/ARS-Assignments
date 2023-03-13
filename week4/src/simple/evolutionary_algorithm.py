from random import random, sample

from .evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism
from .selection import tournament_selection


class EvolutionaryAlgorithm:
    population: list[EvolutionaryAlgorithmOrganism]
    fitness: list[float]
    population_size: int
    survival_rate: float
    best_organism: EvolutionaryAlgorithmOrganism
    best_fitness: float
    generation_count:int
    org_fit_list: list[tuple[EvolutionaryAlgorithmOrganism, float]]

    def __init__(
        self,
        population_size=20,
        survival_rate=0.2,
        *,
        input: int,
        hidden: list[int] = [],
        output: int,
    ) -> None:
        self.generation_count = 0
        self.population_size = population_size
        self.survival_rate = survival_rate
        self.population = [
            EvolutionaryAlgorithmOrganism(input=input, hidden=hidden, output=output)
            for _ in range(population_size)
        ]
        self.best_organism = self.population[0]
        self.best_fitness = float("inf")
        self.not_in_timer = 0

    def epoch(self, input_robots, bench):
        self.org_fit_list = [(ea, bench(input_robots[i])) for i, ea in enumerate(self.population)]
        self.fitness = self.__calc_fitness(input_robots, bench)
        self.__update_global_best()

    def __calc_fitness(self, input_robots, bench):
        return [bench(input_robots[i]) for i, ea in enumerate(self.population)]

    def repopulate(self, timer=5):
        new_p = breed(self.population_size, self.population)
        mutate(self.population)
        self.population += new_p
        self.generation_count += 1


        if self.not_in_timer > timer and self.best_organism not in self.population:
            self.__add_best_again()
            self.not_in_timer = 0
        self.not_in_timer += self.best_organism not in self.population

    def __add_best_again(self, n=1):
        self.population[-n:] = [self.best_organism.copy() for _ in range(n)]

    def diversity(self) -> float:
        return calc_whole_diversity(self.population)

    def best(self, n=1) -> list[EvolutionaryAlgorithmOrganism]:
        sorted_best = self.__sorted_population_fitness_list()[:n]
        return [ea for ea, _ in sorted_best]

    def __update_global_best(self):
        ea, fitness = sorted(self.org_fit_list, key=lambda x: x[1])[0]
        if fitness < self.best_fitness:
            self.best_organism = ea.copy()
            self.best_fitness = fitness

    def selection(self):
        size = int(self.population_size * self.survival_rate)
        self.population = tournament_selection(self.__population_fitness_list(), size)

    def __population_fitness_list(
        self,
    ) -> list[tuple[EvolutionaryAlgorithmOrganism, float]]:
        return list(zip(self.population, self.fitness))

    def __sorted_population_fitness_list(
        self,
    ) -> list[tuple[EvolutionaryAlgorithmOrganism, float]]:
        return sorted(self.__population_fitness_list(), key=lambda x: x[1])


def calc_single_diversity(
    ea: EvolutionaryAlgorithmOrganism, ea_list: list[EvolutionaryAlgorithmOrganism]
) -> float:
    return sum([ea.difference(o) for o in ea_list])


def calc_whole_diversity(list: list[EvolutionaryAlgorithmOrganism]) -> float:
    total = 0
    for i, p in enumerate(list):
        total += calc_single_diversity(p, list[i:])
    return total


def breed(size: int, population: list[EvolutionaryAlgorithmOrganism]):
    offspring = []
    while len(offspring) < (size - len(population)):
        x, y = sample(population, 2)
        b = x.cross(y)
        offspring.append(b)
    return offspring


def mutate(
    population: list[EvolutionaryAlgorithmOrganism],
    mutation_scaler: float = 1.0,
    organism_mutation_chance: float = 1.0,
    weight_mutation_chance=1.0,
):
    for p in population:
        if random() < organism_mutation_chance:
            p.mutate(mutation_scaler, weight_mutation_chance)
