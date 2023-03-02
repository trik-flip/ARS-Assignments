from random import random, sample

from connection import Connection
from node import Node
from organism import Organism
from species import Species


class NEAT:
    generation = 0
    species: list[Species]
    organisms: list[Organism]
    connections: list[Connection]
    nodes: list[Node]
    survival_rate = 0.7
    target_number_of_organisms = 120

    def __init__(self, task) -> None:
        self.task = task

    def epoch(self):
        self.generation += 1
        self.speciation()
        self.selection()
        self.crossover()
        self.mutation()
        self.repopulate()

    speciation_threshold: float

    def speciation(self):
        self.species = []

        for org in self.organisms:
            min_diff = float("inf")
            best_fit = None
            for s in self.species:
                if (diff := s.speciation_difference(org)) < min_diff:
                    min_diff = diff
                    best_fit = s

            if best_fit is None or min_diff > self.speciation_threshold:
                s = Species(org, len(self.species))
                self._create_species(org)
            else:
                best_fit.add_member(org)

    survival_rate: float

    def selection(self):
        species: dict[int, list[Organism]] = {s.id: [] for s in self.species}
        for org in self.organisms:
            species[org.species_id].append(org)
        all_organisms = []
        for k in species:
            species[k].sort(key=lambda x: x.fitness())
            species[k] = species[k][int(len(species[k]) * self.survival_rate) :]
            all_organisms += species[k]
        for org in all_organisms:
            self._remove_organism(org)

    crossover_change: float
    crossover_winning: float

    def crossover(self):
        babies = []
        while len(self.organisms) < self.population_amount:
            s1, s2 = sample(self.species, 2)
            (o1,) = sample(s1.members, 1)
            (o2,) = sample(s2.members, 1)
            o3 = cross_over(o1, o2)
            babies.append(o3)
        self.new_population = babies

    mutation_chance: float

    def mutation(self):
        for org in self.organisms:
            if random() < self.mutation_chance:
                org.mutate()

    population_amount: int

    def repopulate(self):
        for baby in self.new_population:
            self._add_organism(baby)

    def _remove_organism(self, org: Organism):
        self.species[org.species_id].remove_member(org)
        self.organisms.remove(org)
        del org

    def _add_organism(self, org):
        self.organisms.append(org)

    def _create_species(self, org):
        species_id = len(self.species)
        s = Species(org, species_id)
        self.species.append(s)


def cross_over(org1: Organism, org2: Organism):
    winning_org = None
    losing_org = None
    if org1.fitness() >= org2.fitness():
        winning_org = org1
        losing_org = org2
    else:
        winning_org = org2
        losing_org = org1
    cons = losing_org.disjoint(winning_org)
    cons += winning_org.disjoint(losing_org)
    cons += winning_org.excess(losing_org)
    for con1, con2 in same_connections(winning_org, losing_org):
        if random() > 0.5:
            cons.append(con1)
        else:
            cons.append(con2)
    cons.sort(key=lambda x: x.id)
    baby = Organism()
    baby.connections = cons
    all_nodes: list[Node] = []
    for c in cons:
        all_nodes.append(c.start)
        all_nodes.append(c.end)
    all_nodes.sort(key=lambda x: x.id)
    baby.nodes = all_nodes
    return baby


def same_connections(organism1: Organism, organism2: Organism):
    return zip(organism1.same(organism1), organism2.same(organism1))


connection_database: dict[int, Connection] = {}
