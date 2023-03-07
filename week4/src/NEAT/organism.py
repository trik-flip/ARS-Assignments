from functools import cache
from node import Node
from connection import Connection


class Organism:
    nodes: list[Node]
    connections: list[Connection]
    species_id: int
    generation: int

    def speciation_difference(self, o):
        assert isinstance(o, Organism)

        c1 = 1
        c2 = 1
        c3 = 1

        E = excess(self, o)
        D = disjoint(self, o)
        N = total_length(self, o)
        W = average_weight_difference(self, o)

        delta = (c1 * E) / N + (c2 * D) / N + (c3 * W)

        return delta

    def max_id(self):
        return max(c.id for c in self.connections)

    def connection_count(self):
        return len(self.connections)

    def mutate(self):
        pass

    def _mutation_add_node(self):
        pass

    def _mutation_add_connection(self):
        pass

    def _mutation_enable_disable_connection(self):
        pass

    def _mutation_shift_weigth(self):
        pass

    def _mutation_randomize_weight(self):
        pass

    def disjoint(self, other):
        assert isinstance(other, Organism)
        disjoint_connections: list[Connection] = []
        for con in self.connections:
            if (
                con.id not in [n.id for n in other.connections]
                and con.id < other.max_id()
            ):
                disjoint_connections.append(con)
        return disjoint_connections

    def excess(self, other):
        assert isinstance(other, Organism)
        excess_connections: list[Connection] = []
        for connection in self.connections:
            if (
                connection.id not in [c.id for c in other.connections]
                and connection.id > other.max_id()
            ):
                excess_connections.append(connection)
        return excess_connections

    def same(self, other):
        assert isinstance(other, Organism)
        same_connections: list[Connection] = []
        for node in self.connections:
            if node.id in [n.id for n in other.connections]:
                same_connections.append(node)
        return same_connections

    _fitness: float

    def fitness(self) -> float:
        if self._fitness is None:
            self._fitness = self._calc_fitness()
        return self._fitness


def excess(organism1: Organism, organism2: Organism) -> int:
    """Count the number of excess connections which are specified in one organism but not in the other"""
    assert (
        len(organism1.excess(organism2)) == 0 or len(organism2.excess(organism1)) == 0
    )
    return len(organism1.excess(organism2)) ^ len(organism2.excess(organism1))


def disjoint(organism1: Organism, organism2: Organism) -> int:
    return len(organism1.disjoint(organism2)) + len(organism2.disjoint(organism1))


def total_length(organism1: Organism, organism2: Organism) -> int:
    total = 0
    total += len(organism1.connections)
    total += len(organism2.disjoint(organism1))
    total += len(organism2.excess(organism1))
    return total


def same_connections(organism1: Organism, organism2: Organism):
    return zip(organism1.same(organism1), organism2.same(organism1))


def average_weight_difference(organism1: Organism, organism2: Organism) -> float:
    difference = 0
    counter = 0
    for con1, con2 in same_connections(organism1, organism2):
        counter += 1
        difference += abs(con1.weight - con2.weight)
    return difference / counter


def speciation(organism1: Organism, organism2: Organism):
    c1 = 1
    c2 = 1
    c3 = 1
    E = excess(organism1, organism2)
    D = disjoint(organism1, organism2)
    N = total_length(organism1, organism2)
    W = average_weight_difference(organism1, organism2)
    delta = (c1 * E) / N + (c2 * D) / N + (c3 * W)
    return delta
