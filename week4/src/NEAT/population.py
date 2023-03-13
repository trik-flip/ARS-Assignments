from random import random
from genome import Genome
from innovation import Innovation
from organism import Organism
from species import Species
from genome import Mutator

babies_stolen = 8
dropoff_age = 6
pop_size = 20
compat_threshold = 0.8


class Population:
    def spawn(self, g: Genome, size: int):
        new_genome: Genome | None = None
        new_organism: Organism

        for i in range(size):
            new_genome = g.duplicate(i + 1)
            new_genome.mutate_link_weights(1.0, 1.0, Mutator.COLDGAUSSIAN)
            new_genome.randomize_traits()
            new_organism = Organism(0.0, new_genome, 1)
            self.organisms.append(new_organism)

        assert new_genome is not None
        self.current_node_id = new_genome.get_last_node_id()
        self.current_innovation_number = new_genome.get_last_gene_innovation_number()

        self.speciate()

        return True

    organisms: list[Organism]

    species: list[Species]

    innovations: list[Innovation]
    current_node_id: int
    current_innovation_number: float

    last_species: int

    mean_fitness: float
    variance: float
    standard_deviation: float

    winner_gen: int

    highest_fitness: float
    highest_last_changed: int

    def speciate(self):
        comp_org: Organism | None = None
        new_species: Species

        counter = 0

        for org in self.organisms:
            species = 0
            if species == len(self.species) - 1:
                counter += 1
                new_species = Species(counter)
                self.species.append(new_species)
                new_species.add_organism(org)
                org.species = new_species
            else:
                comp_org = self.species[species].first()
                while (comp_org is not None) and (species != len(self.species) - 1):
                    if (org.gnome.compatibility(comp_org.gnome)) < compat_threshold:
                        self.species[species].add_organism(org)
                        org.species = self.species[species]
                        comp_org = None
                    else:
                        species += 1
                        if species != len(self.species) - 1:
                            comp_org = self.species[species].first()

                if comp_org is not None:
                    counter += 1
                    new_species = Species(counter)
                    self.species.append(new_species)
                    new_species.add_organism(org)
                    org.species = new_species

        self.last_species = counter

        return True

    def verify(self):
        verification = None
        for org in self.organisms:
            verification = org.gnome.verify()

        assert verification is not None
        return verification

    def epoch(self, generation: int):
        total = 0.0

        overall_average: float

        orgcount: int

        skim: float
        total_exp: int
        total_organisms = len(self.organisms)
        max_exp: int
        best_species: Species | None = None
        final_exp: int

        NUM_STOLEN = babies_stolen
        one_fifth_stolen: int
        one_tenth_stolen: int

        # sorted species
        ss: list[Species] = []
        stolen_babies: int

        half_pop: int

        best_species_num: int

        for s in self.species:
            ss.append(s)

        ss.sort(key=lambda x: x.organisms[0].original_fitness)

        species = len(ss) - 2
        while species is not None and ss[species].age < 20:
            species -= 1
        if (generation % 30) == 0:
            ss[species].obliterate = True

        for species in self.species:
            species.adjust_fitness()

        total = sum([org.fitness for org in self.organisms])
        overall_average = total / total_organisms

        for org in self.organisms:
            org.expected_offspring = org.fitness / overall_average

        skim = 0.0
        total_exp = 0
        for species in self.species:
            skim = species.count_offspring(skim)
            total_exp += species.expected_offspring

        if total_exp < total_organisms:
            max_exp = 0
            final_exp = 0
            for species in self.species:
                if species.expected_offspring >= max_exp:
                    max_exp = species.expected_offspring
                    best_species = species
                final_exp += species.expected_offspring
            assert best_species is not None
            best_species.expected_offspring += 1
            final_exp += 1

            if final_exp < total_organisms:
                for species in self.species:
                    species.expected_offspring = 0
                best_species.expected_offspring = total_organisms

        ss.sort(key=lambda x: x.organisms[0].original_fitness)

        best_species_num = ss[0].id

        species = ss[0]
        species.organisms[0].pop_champ = True
        if species.organisms[0].original_fitness > self.highest_fitness:
            self.highest_fitness = species.organisms[0].original_fitness
            self.highest_last_changed = 0
        else:
            self.highest_last_changed += 1

        if self.highest_last_changed >= dropoff_age + 5:
            self.highest_last_changed = 0

            half_pop = pop_size // 2

            species = 0

            ss[species].organisms[0].super_champ_offspring = half_pop
            ss[species].expected_offspring = half_pop
            ss[species].age_of_last_improvement = ss[species].age

            species += 1

            if ss[species] != ss[-1]:
                ss[species].organisms[0].super_champ_offspring = pop_size - half_pop
                ss[species].expected_offspring = pop_size - half_pop
                ss[species].age_of_last_improvement = ss[species].age

                species += 1

                while ss[species] != ss[-1]:
                    ss[species].expected_offspring = 0
                    species += 1
            else:
                species = 0
                ss[species].organisms[0].super_champ_offspring += pop_size - half_pop
                ss[species].expected_offspring = pop_size - half_pop
        elif babies_stolen > 0:
            stolen_babies = 0
            species = len(ss) - 2
            while stolen_babies < NUM_STOLEN and ss[species] != ss[0]:
                if ss[species].age > 5 and ss[species].expected_offspring > 2:
                    if ss[species].expected_offspring - 1 >= NUM_STOLEN - stolen_babies:
                        ss[species].expected_offspring -= NUM_STOLEN - stolen_babies
                        stolen_babies = NUM_STOLEN
                    else:
                        stolen_babies += ss[species].expected_offspring - 1
                        ss[species].expected_offspring = 1

                species -= 1

            species = 0

            one_fifth_stolen = babies_stolen // 5
            one_tenth_stolen = babies_stolen // 10

            while species != len(ss) - 1 and ss[species].last_improved() > dropoff_age:
                species += 1

            if stolen_babies >= one_fifth_stolen and ss[species] != ss[-1]:
                ss[species].organisms[0].super_champ_offspring = one_fifth_stolen
                ss[species].expected_offspring += one_fifth_stolen
                stolen_babies -= one_fifth_stolen

                species += 1

            while species != len(ss) - 1 and ss[species].last_improved() > dropoff_age:
                species += 1

            if ss[species] != ss[-1] and stolen_babies >= one_fifth_stolen:
                ss[species].organisms[0].super_champ_offspring = one_fifth_stolen
                ss[species].expected_offspring += one_fifth_stolen
                stolen_babies -= one_fifth_stolen
                species += 1

            while ss[species] != ss[-1] and ss[species].last_improved() > dropoff_age:
                species += 1

            if ss[species] != ss[-1] and stolen_babies >= one_tenth_stolen:
                ss[species].organisms[0].super_champ_offspring = one_tenth_stolen
                ss[species].expected_offspring += one_tenth_stolen
                stolen_babies -= one_tenth_stolen

                species += 1

            while ss[species] != ss[-1] and ss[species].last_improved() > dropoff_age:
                species += 1

            while stolen_babies > 0 and ss[species] != ss[-1]:
                if random() > 0.1:
                    if stolen_babies > 3:
                        ss[species].organisms[0].super_champ_offspring = 3
                        ss[species].expected_offspring += 3
                        stolen_babies -= 3
                    else:
                        ss[species].organisms[0].super_champ_offspring = stolen_babies
                        ss[species].expected_offspring += stolen_babies
                        stolen_babies = 0

                species += 1

                while (
                    ss[species] != ss[-1] and ss[species].last_improved() > dropoff_age
                ):
                    species += 1

            if stolen_babies > 0:
                species = 0
                ss[species].organisms[0].super_champ_offspring += stolen_babies
                ss[species].expected_offspring += stolen_babies
                stolen_babies = 0

        org = 0
        while org != len(self.organisms):
            if self.organisms[org].eliminate:
                self.organisms[org].species.remove_org(self.organisms[org])

                del self.organisms[org]

                dead_org = org

                self.organisms.remove(self.organisms[dead_org])
            org += 1

        species = 0
        last_id = self.species[species].id
        while self.species[species] != self.species[-1]:
            self.species[species].reproduce(generation, self, ss)

            curspecies2 = 0
            while self.species[curspecies2] != self.species[-1]:
                if self.species[curspecies2].id == last_id:
                    species = curspecies2
                curspecies2 += 1

            species += 1

            if self.species[species] != self.species[-1]:
                last_id = self.species[species].id

        org = 0
        while self.organisms[org] != self.organisms[-1]:
            self.organisms[org].species.remove_org(self.organisms[org])

            del self.organisms[org]

            dead_org = org
            org += 1

            self.organisms.remove(self.organisms[dead_org])

        species = 0
        orgcount = 0
        while self.species[species] != self.species[-1]:
            if len(self.species[species].organisms) == 0:
                del self.species[species]

                deadspecies = species
                species += 1

                self.species.remove(self.species[deadspecies])
            else:
                if self.species[species].novel:
                    self.species[species].novel = False
                else:
                    self.species[species].age += 1

                for org in self.species[species].organisms:
                    org.gnome.genome_id = orgcount
                    orgcount += 1
                    self.organisms.append(org)
                species += 1

        curinnov = 0
        while self.innovations[curinnov] != self.innovations[-1]:
            del self.innovations[curinnov]

            deadinnov = curinnov
            curinnov += 1

            self.innovations.remove(self.innovations[deadinnov])

        return True

    def rank_within_species(self):
        for species in self.species:
            species.rank()

        return True

    @staticmethod
    def create_population_single_genome(g: Genome, size: int):
        pop = Population()
        pop.winner_gen = 0
        pop.highest_fitness = 0.0
        pop.highest_last_changed = 0
        pop.spawn(g, size)
        return pop

    @staticmethod
    def create_population_without_mutation(g: Genome, size: int, power: float):
        pop = Population()
        pop.winner_gen = 0
        pop.highest_fitness = 0.0
        pop.highest_last_changed = 0
        pop.clone(g, size, power)
        return pop

    @staticmethod
    def create_population_genomes(genome_list: list[Genome], power: float):
        pop = Population()
        pop.winner_gen = 0
        pop.highest_fitness = 0.0
        pop.highest_last_changed = 0
        new_genome: Genome | None = None
        for iter in genome_list:
            new_genome = iter
            if power > 0:
                new_genome.mutate_link_weights(power, 1.0, Mutator.GAUSSIAN)
            new_genome.randomize_traits()
            new_organism = Organism(0.0, new_genome, 1)
            pop.organisms.append(new_organism)

        assert new_genome is not None
        pop.current_node_id = new_genome.get_last_node_id()
        pop.current_innovation_number = new_genome.get_last_gene_innovation_number()

        pop.speciate()
        return pop

    def clone(self, g: Genome, size: int, power: float):
        new_genome = g.duplicate(1)
        new_organism = Organism(0.0, new_genome, 1)
        self.organisms.append(new_organism)

        count = 2
        while count <= size:
            new_genome = g.duplicate(count)
            if power > 0:
                new_genome.mutate_link_weights(power, 1.0, Mutator.GAUSSIAN)

            new_genome.randomize_traits()
            new_organism = Organism(0.0, new_genome, 1)
            self.organisms.append(new_organism)
            count += 1

        self.current_node_id = new_genome.get_last_node_id()
        self.current_innovation_number = new_genome.get_last_gene_innovation_number()

        self.speciate()

        return True
