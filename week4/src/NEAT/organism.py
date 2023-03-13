from species import Species
from genome import Genome
from network import Network


class Organism:
    fitness: float
    original_fitness: float
    error: float
    winner: bool
    net: Network
    gnome: Genome
    species: Species | None
    expected_offspring: float
    generation: int
    eliminate: bool
    champion: bool
    super_champ_offspring: int
    pop_champ: bool
    pop_champ_child: bool
    high_fit: float
    time_alive: int

    # // Track its origin- for debugging or analysis- we can tell how the organism was born
    mut_struct_baby: bool
    mate_baby: bool

    # // MetaData for the object
    metadata: str
    modified: bool

    def __init__(self, fit: float, g: Genome, gen: int, md: str = ""):
        self.fitness = fit
        self.original_fitness = self.fitness
        self.gnome = g
        self.net = self.gnome.genesis(self.gnome.genome_id)
        self.species = None  # Start it in no Species
        self.expected_offspring = 0
        self.generation = gen
        self.eliminate = False
        self.error = 0
        self.winner = False
        self.champion = False
        self.super_champ_offspring = 0

        # // If md is null, then we don't have metadata, otherwise we do have metadata so copy it over
        self.metadata = md

        self.time_alive = 0

        self.pop_champ = False
        self.pop_champ_child = False
        self.high_fit = 0
        self.mut_struct_baby = False
        self.mate_baby = False

        self.modified = True

    # // Regenerate the network based on a change in the genotype
    def update_phenotype(self):
        self.net = self.gnome.genesis(self.gnome.genome_id)
        self.modified = True


def order_orgs(x: Organism, y: Organism) -> bool:
    return x.fitness > y.fitness


def order_orgs_by_adjusted_fit(x: Organism, y: Organism) -> bool:
    return adjusted_fit(x) > adjusted_fit(y)


def adjusted_fit(x):
    return x.fitness / x.species.organisms.size()
