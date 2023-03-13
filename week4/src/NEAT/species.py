from math import fmod
from random import randint, random
from typing import Self
from organism import Organism
from genome import Genome, Mutator
from network import Network
from population import Population, compat_threshold

dropoff_age = 8
age_significance = 2
survival_thresh = 0.6
mutate_add_link_prob = 0.4
newlink_tries = 3
weight_mut_power = 4
mutate_add_node_prob = 0.3
interspecies_mate_rate = 0.2
mate_only_prob = 0.1
mutate_random_trait_prob = 0.3
mutate_link_trait_prob = 0.3
mutate_node_trait_prob = 0.3
mutate_link_weights_prob = 0.3
mutate_toggle_enable_prob = 0.3
mutate_gene_reenable_prob = 0.3
mate_multipoint_avg_prob = 0.5
mate_multipoint_prob = 0.5
mate_singlepoint_prob = 0.3
mutate_only_prob = 0.5


class Species:
    id: int
    age: int
    ave_fitness: float
    max_fitness: float
    max_fitness_ever: float
    expected_offspring: int
    novel: bool
    checked: bool
    obliterate: bool
    organisms: list[Organism]
    age_of_last_improvement: int
    average_est: float

    def add_organism(self, o: Organism):
        self.organisms.append(o)
        return True

    def first(self):
        return self.organisms[0]

    def adjust_fitness(self):
        num_parents: int
        age_debt: int
        age_debt = (self.age - self.age_of_last_improvement + 1) - dropoff_age

        if age_debt == 0:
            age_debt = 1

        for org in self.organisms:
            org.original_fitness = org.fitness

            if age_debt >= 1 or self.obliterate:
                org.fitness *= 0.01

            if self.age <= 10:
                org.fitness = org.fitness * age_significance

            if org.fitness < 0.0:
                org.fitness = 0.0001

            org.fitness = org.fitness / (len(self.organisms))

        self.organisms.sort(key=lambda x: x.fitness)

        if self.organisms[0].original_fitness > self.max_fitness_ever:
            self.age_of_last_improvement = self.age
            self.max_fitness_ever = self.organisms[0].original_fitness

        num_parents = int(survival_thresh * len(self.organisms)) + 1

        org = 0
        self.organisms[org].champion = True
        for _ in range(num_parents):
            if org != len(self.organisms):
                org += 1

        while org != len(self.organisms):
            self.organisms[org].eliminate = True
            org += 1

    def compute_average_fitness(self):
        total = 0.0

        for org in self.organisms:
            total += org.fitness

        ave_fitness = total / len(self.organisms)

        return ave_fitness

    def compute_max_fitness(self) -> float:
        max_fitness = max([org.fitness for org in self.organisms])

        self.max_fitness = max_fitness

        return max_fitness

    def count_offspring(self, skim: float) -> float:
        e_o_intpart: int
        e_o_fracpart: float
        skim_intpart: float

        expected_offspring = 0

        for curorg in self.organisms:
            e_o_intpart = int(curorg.expected_offspring)
            e_o_fracpart = fmod(curorg.expected_offspring, 1.0)

            expected_offspring += e_o_intpart

            skim += e_o_fracpart

            if skim > 1.0:
                skim_intpart = int(skim)
                expected_offspring += int(skim_intpart)
                skim -= skim_intpart

        return skim

    def last_improved(self):
        return self.age - self.age_of_last_improvement

    def remove_org(self, org: Organism):
        curorg = 0
        while (self.organisms[curorg] != self.organisms[-1]) and (
            self.organisms[curorg] != org
        ):
            curorg += 1

        if self.organisms[curorg] == self.organisms[-1]:
            return False
        else:
            self.organisms.remove(self.organisms[curorg])
            return True

    def size(self):
        return len(self.organisms)

    def get_champ(self):
        champ_fitness = -1.0
        champ = None
        for org in self.organisms:
            if org.fitness > champ_fitness:
                champ = org
                champ_fitness = champ.fitness
        assert champ is not None
        return champ

    def reproduce(self, generation: int, pop: Population, sorted_species: list[Self]):
        count: int
        pool_size: int
        org_num: int
        mom: Organism
        dad: Organism
        baby: Organism
        new_genome: Genome
        new_species: Species
        comp_org: Organism
        rand_species: Species
        rand_mult: float
        rand_species_num: int
        net_analogue: Network
        outside: bool
        found: bool
        champ_done = False
        champ: Organism
        give_up: int
        mut_struct_baby: bool
        mate_baby: bool
        mut_power = weight_mut_power
        if self.expected_offspring > 0 and len(self.organisms) == 0:
            return False
        pool_size = len(self.organisms) - 1
        champ = self.organisms[0]
        for count in range(self.expected_offspring):
            mut_struct_baby = False
            mate_baby = False
            outside = False
            if champ.super_champ_offspring > 0:
                mom = champ
                new_genome = mom.gnome.duplicate(count)

                if (champ.super_champ_offspring) > 1:
                    if random() < 0.8 or mutate_add_link_prob == 0.0:
                        new_genome.mutate_link_weights(mut_power, 1.0, Mutator.GAUSSIAN)
                    else:
                        net_analogue = new_genome.genesis(generation)
                        new_genome.mutate_add_link(
                            pop.innovations,
                            pop.current_innovation_number,
                            newlink_tries,
                        )
                        del net_analogue
                        self.mut_struct_baby = True

                baby = Organism(0.0, new_genome, generation)

                if champ.super_champ_offspring == 1 and champ.pop_champ:
                    baby.pop_champ_child = True
                    baby.high_fit = mom.original_fitness

                champ.super_champ_offspring -= 1
            elif not champ_done and self.expected_offspring > 5:
                mom = champ

                new_genome = mom.gnome.duplicate(count)

                baby = Organism(0.0, new_genome, generation)

                champ_done = True
            elif random() < mutate_only_prob or pool_size == 0:
                org_num = randint(0, pool_size)
                curorg = 0
                curorg = org_num

                mom = self.organisms[curorg]

                new_genome = mom.gnome.duplicate(count)

                if random() < mutate_add_node_prob:
                    new_genome.mutate_add_node(
                        pop.innovations,
                        pop.current_node_id,
                        pop.current_innovation_number,
                    )
                    self.mut_struct_baby = True

                elif random() < mutate_add_link_prob:
                    net_analogue = new_genome.genesis(generation)
                    new_genome.mutate_add_link(
                        pop.innovations, pop.current_innovation_number, newlink_tries
                    )
                    del net_analogue
                    self.mut_struct_baby = True
                else:
                    if random() < mutate_random_trait_prob:
                        new_genome.mutate_random_trait()
                    if random() < mutate_link_trait_prob:
                        new_genome.mutate_link_trait(1)
                    if random() < mutate_node_trait_prob:
                        new_genome.mutate_node_trait(1)
                    if random() < mutate_link_weights_prob:
                        new_genome.mutate_link_weights(mut_power, 1.0, Mutator.GAUSSIAN)
                    if random() < mutate_toggle_enable_prob:
                        new_genome.mutate_toggle_enable(1)
                    if random() < mutate_gene_reenable_prob:
                        new_genome.mutate_gene_reenable()

                baby = Organism(0.0, new_genome, generation)

            else:
                org_num = randint(0, pool_size)
                curorg = org_num

                mom = self.organisms[curorg]

                if random() > interspecies_mate_rate:
                    org_num = randint(0, pool_size)
                    curorg = 0
                    curorg += org_num

                    dad = self.organisms[curorg]
                else:
                    rand_species = self

                    give_up = 0
                    while (rand_species == self) and (give_up < 5):
                        rand_mult = gaussrand() / 4
                        if rand_mult > 1.0:
                            rand_mult = 1.0
                        rand_species_num = int(
                            (rand_mult * (len(sorted_species) - 1.0)) + 0.5
                        )
                        cur_sp = rand_species_num
                        rand_species = sorted_species[cur_sp]

                        give_up += 1

                    dad = rand_species.organisms[0]

                    self.outside = True

                if random() < mate_multipoint_prob:
                    new_genome = mom.gnome.mate_multipoint(
                        dad.gnome,
                        count,
                        mom.original_fitness,
                        dad.original_fitness,
                        outside,
                    )
                elif random() < (
                    mate_multipoint_avg_prob
                    / (mate_multipoint_avg_prob + mate_singlepoint_prob)
                ):
                    new_genome = mom.gnome.mate_multipoint_avg(
                        dad.gnome,
                        count,
                        mom.original_fitness,
                        dad.original_fitness,
                        outside,
                    )
                else:
                    new_genome = mom.gnome.mate_singlepoint(dad.gnome, count)

                mate_baby = True

                if (
                    random() > mate_only_prob
                    or dad.gnome.genome_id == mom.gnome.genome_id
                    or dad.gnome.compatibility(mom.gnome) == 0.0
                ):
                    if random() < mutate_add_node_prob:
                        new_genome.mutate_add_node(
                            pop.innovations,
                            pop.current_node_id,
                            pop.current_innovation_number,
                        )
                        mut_struct_baby = True
                    elif random() < mutate_add_link_prob:
                        net_analogue = new_genome.genesis(generation)
                        new_genome.mutate_add_link(
                            pop.innovations,
                            pop.current_innovation_number,
                            newlink_tries,
                        )
                        del net_analogue
                        mut_struct_baby = True
                    else:
                        if random() < mutate_random_trait_prob:
                            new_genome.mutate_random_trait()
                        if random() < mutate_link_trait_prob:
                            new_genome.mutate_link_trait(1)
                        if random() < mutate_node_trait_prob:
                            new_genome.mutate_node_trait(1)
                        if random() < mutate_link_weights_prob:
                            new_genome.mutate_link_weights(
                                mut_power, 1.0, Mutator.GAUSSIAN
                            )
                        if random() < mutate_toggle_enable_prob:
                            new_genome.mutate_toggle_enable(1)
                        if random() < mutate_gene_reenable_prob:
                            new_genome.mutate_gene_reenable()

                baby = Organism(0.0, new_genome, generation)

            baby.mut_struct_baby = mut_struct_baby
            baby.mate_baby = mate_baby

            cur_species = 0
            if pop.species[cur_species] == pop.species[-1]:
                pop.last_species += 1
                new_species = Species(pop.last_species, True)
                pop.species.append(new_species)
                new_species.add_organism(baby)
                baby.species = new_species
            else:
                comp_org = pop.species[cur_species].first()
                found = False
                while cur_species != len(pop.species) and not found:
                    if comp_org == 0:
                        cur_species += 1
                        if cur_species != pop.species[-1]:
                            comp_org = pop.species[cur_species].first()
                    elif baby.gnome.compatibility(comp_org.gnome) < compat_threshold:
                        pop.species[cur_species].add_organism(baby)
                        baby.species = pop.species[cur_species]
                        found = True
                    else:
                        cur_species += 1
                        if pop.species[cur_species] != pop.species[-1]:
                            comp_org = pop.species[cur_species].first()

                if not found:
                    pop.last_species += 1
                    new_species = Species(pop.last_species, True)
                    pop.species.append(new_species)
                    new_species.add_organism(baby)
                    baby.species = new_species

        return True

    def rank(self):
        self.organisms.sort(key=lambda x: x.fitness)
        return True

    def __init__(self, i: int, n: bool = False):
        self.id = i
        self.age = 1
        self.ave_fitness = 0.0
        self.expected_offspring = 0
        self.novel = n
        self.age_of_last_improvement = 0
        self.max_fitness = 0
        self.max_fitness_ever = 0
        self.obliterate = False

        self.average_est = 0


def order_species(x: Species, y: Species):
    return x.organisms[0].original_fitness > y.organisms[0].original_fitness


def order_new_species(x: Species, y: Species):
    return x.compute_max_fitness() > y.compute_max_fitness()
