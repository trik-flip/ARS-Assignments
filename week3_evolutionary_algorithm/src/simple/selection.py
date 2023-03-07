from random import random
from .evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism


def roulette_wheel_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    new_pop: list[EvolutionaryAlgorithmOrganism] = []
    fitness = [f for _, f in population]
    max_fitness = max(fitness) + 1
    total_chance = sum(fitness) + len(fitness)

    accumulated_chance = [(ea, max_fitness - f) for ea, f in population]

    while size > len(new_pop):
        counting_chance = 0
        counter = 0
        selection = None

        random_pick = random() * total_chance

        while random_pick > counting_chance:
            selection = accumulated_chance[counter][0]
            counting_chance += accumulated_chance[counter][1]
            counter += 1

        assert selection is not None
        new_pop.append(selection)

    return new_pop


def unique_roulette_wheel_selection(
    population, size
) -> list[EvolutionaryAlgorithmOrganism]:
    new_pop: set[EvolutionaryAlgorithmOrganism] = set()
    fitness = [f for _, f in population]
    max_fitness = max(fitness) + 1
    total_chance = sum(fitness) + len(fitness)

    accumulated_chance = [(ea, max_fitness - f) for ea, f in population]

    while size > len(new_pop):
        counting_chance = 0
        counter = 0
        selection = None

        random_pick = random() * total_chance

        while random_pick > counting_chance:
            selection = accumulated_chance[counter][0]
            counting_chance += accumulated_chance[counter][1]
            counter += 1

        assert selection is not None
        new_pop.add(selection)

    return list(new_pop)


def elitist_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    return [ea for ea, _ in sorted(population, key=lambda x: x[1])[:size]]


def rank_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Rank_Selection
    pass


def steady_state_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Steady_State_Selection
    pass


def tournament_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Tournament_Selection
    pass


def boltzmann_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Boltzmann_Selection
    pass


def diversity_selection(population, size) -> list[EvolutionaryAlgorithmOrganism]:
    # TODO: rank based on fitness and diversity
    pass
