from random import random, sample

from .evolutionary_algorithm_organism import EvolutionaryAlgorithmOrganism

PopAndFitnessType = list[tuple[EvolutionaryAlgorithmOrganism, float]]
EAOListType = list[EvolutionaryAlgorithmOrganism]


def roulette_wheel_selection(population: PopAndFitnessType, size) -> EAOListType:
    new_pop: EAOListType = []
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


def unique_roulette_wheel_selection(population: PopAndFitnessType, size) -> EAOListType:
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


def elitist_selection(population: PopAndFitnessType, size) -> EAOListType:
    return [ea for ea, _ in sorted(population, key=lambda x: x[1])[:size]]


def rank_selection(population: PopAndFitnessType, size) -> EAOListType:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Rank_Selection
    pass


def tournament_selection(
    population: PopAndFitnessType, size, K=10, p=0.6
) -> EAOListType:
    # https://en.wikipedia.org/wiki/Selection_(genetic_algorithm)#Tournament_Selection
    new_pop = []

    tournament = sample(population, K)
    accumulated_chance = [
        (ea, p * ((1 - p) ** i))
        for i, (ea, _) in enumerate(sorted(tournament, key=lambda x: x[1]))
    ]
    total_chance = sum([f for _, f in accumulated_chance])

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

    return list(new_pop)


def diversity_selection(population: PopAndFitnessType, size) -> EAOListType:
    pass
