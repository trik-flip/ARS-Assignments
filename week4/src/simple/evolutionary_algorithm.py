import pickle
from random import random, sample

from .evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism
from .selection import (
    elitist_selection, tournament_selection,
)


class EvolutionaryAlgorithm:
    population: list[EvolutionaryAlgorithmOrganism]
    fitness: list[float]
    population_size: int
    survival_rate: float
    best_organism: EvolutionaryAlgorithmOrganism
    best_fitness: float
    generation_count: int
    org_fit_list: list[tuple[EvolutionaryAlgorithmOrganism, float]]

    @staticmethod
    def load(filename: str):
        with open(filename, "rb") as f:
            ea = pickle.load(f)
        assert isinstance(ea, EvolutionaryAlgorithm)
        return ea

    def __init__(
        self,
        population_size=20,
        survival_rate=0.2,
        *,
        input: int,
        hidden: list[int] = [],
        output: int,
        recur: int | None = None,
        mutation_rate: float = 1,
        mutation_chance: float = 1
    ) -> None:
        self.mutation_rate = mutation_rate
        self.mutation_chance = mutation_chance

        self.no_better_counter = 0
        self.generation_count = 0
        self.population_size = population_size
        self.survival_rate = survival_rate
        self.population = [
            EvolutionaryAlgorithmOrganism(
                input=input, hidden=hidden, output=output, recur=recur
            )
            for _ in range(population_size)
        ]
        self.best_organism = self.population[0]
        self.best_fitness = float("inf")
        self.not_in_timer = 0

    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    def epoch(self, input_robots, bench):
        self.org_fit_list = [
            (ea, bench(input_robots[i])) for i, ea in enumerate(self.population)
        ]
        self.fitness = self.__calc_fitness(input_robots, bench)
        self.__update_global_best()

    def __calc_fitness(self, input_robots, bench):
        return [bench(input_robots[i]) for i, _ in enumerate(self.population)]

    def repopulate(self, timer=5):
        new_p = breed(self.population_size, self.population)
        mutate(self.population, self.mutation_rate, self.mutation_chance)
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
            self.no_better_counter = 0
        else:
            self.no_better_counter += 1

    def selection(self):
        size = int(self.population_size * self.survival_rate)
        self.population = tournament_selection(self.__population_fitness_list(), size)

    def __population_fitness_list(
        self,
    ) -> list[tuple[EvolutionaryAlgorithmOrganism, float]]:
        return list(zip(self.population, self.fitness))

    def sorted_population(
        self,
    ) -> list[EvolutionaryAlgorithmOrganism]:
        return [
            ea for ea, _ in sorted(self.__population_fitness_list(), key=lambda x: x[1])
        ]

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
