from random import randint, random, sample

from gene import Gene
from innovation import Innovation
from link import Link
from mutator import Mutator
from neat import rand_pos_neg
from network import Network
from nnode import NNode, NodePlace, NodeType
from trait import Trait
from util import select_random
from innovation_type import InnovationType

disjoint_coefficient = 0.5
excess_coefficient = 0.5
mutation_diff_coefficient = 0.5
recur_only_prob = 0.3


class Genome:
    genome_id: int

    traits: list[Trait]
    nodes: list[NNode]
    genes: list[Gene]

    phenotype: Network

    # Constructor which takes full genome specs and puts them into the new one
    @staticmethod
    def create_full_genome_specs(
        id: int, t: list[Trait], n: list[NNode], g: list[Gene]
    ):
        gen = Genome()
        gen.genome_id = id
        gen.traits = t
        gen.nodes = n
        gen.genes = g
        return gen

    # Constructor which takes in links (not genes) and creates a Genome
    @staticmethod
    def create_incomplete_genome_specs(
        id: int, t: list[Trait], n: list[NNode], links: list[Link]
    ):
        gen = Genome()
        gen.traits = t
        gen.nodes = n
        gen.genome_id = id

        # We go through the links and turn them into original genes
        for link in links:
            # Create genes one at a time
            temp_gene = Gene.create_a_trait(
                link.link_trait,
                link.weight,
                link.in_node,
                link.out_node,
                link.is_recurrent,
                1.0,
                0.0,
            )
            gen.genes.append(temp_gene)

    # This special constructor creates a Genome
    # with i inputs, o outputs, n out of n_max hidden units, and random
    # connectivity.  If r is True then recurrent connections will
    # be included.
    @staticmethod
    def create_special(
        new_id: int, i: int, o: int, n: int, n_max: int, r: bool, link_prob: float
    ):
        G = Genome()
        total_nodes: int
        cm_ptr: int
        matrix_dim: int
        count: int
        c: int
        row: int
        col: int
        new_weight: float
        max_node: int
        first_output: int
        total_nodes = i + o + n_max
        matrix_dim = total_nodes * total_nodes
        cm: list[bool] = []
        max_node = i + n
        first_output = total_nodes - o + 1
        node: NNode
        new_gene: Gene
        new_trait: Trait
        in_node: NNode
        out_node: NNode
        G.genome_id = new_id
        cm_ptr = 0
        for count in range(matrix_dim):
            cm[cm_ptr] = random() < link_prob
            cm_ptr += 1

        new_trait = Trait.create_from_manual(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        G.traits.append(new_trait)

        for node in Genome.add_input_nodes(i, G):
            node.node_trait = new_trait
        for node in Genome.add_hidden_nodes(i, n, G):
            node.node_trait = new_trait
        for node in Genome.add_output_nodes(G, total_nodes, first_output):
            node.node_trait = new_trait

        count = 0
        for col in range(1, 1 + total_nodes):
            for row in range(1, total_nodes + 1):
                if (
                    cm[count]
                    and col > i
                    and (col <= max_node or col >= first_output)
                    and (row <= max_node or row >= first_output)
                ):
                    node_iter = Genome._find_node(G, row)
                    in_node = G.nodes[node_iter]

                    node_iter = Genome._find_node(G, col)
                    out_node = G.nodes[node_iter]

                    new_weight = rand_pos_neg() * random()
                    if col > row:
                        new_gene = Gene.create_a_trait(
                            new_trait,
                            new_weight,
                            in_node,
                            out_node,
                            False,
                            count,
                            new_weight,
                        )
                        G.genes.append(new_gene)
                    elif r:
                        new_gene = Gene.create_a_trait(
                            new_trait,
                            new_weight,
                            in_node,
                            out_node,
                            True,
                            count,
                            new_weight,
                        )
                        G.genes.append(new_gene)

                count += 1
        return G

    @staticmethod
    def _find_node(G, row):
        node_iter = 0
        while G.nodes[node_iter].node_id != row:
            node_iter += 1
        return node_iter

    @staticmethod
    def add_output_nodes(G, total_nodes, first_output):
        for c in range(total_nodes - (first_output - 1)):
            node = NNode.create_from_nodetype(
                NodeType.NEURON, c + first_output + 1, NodePlace.OUTPUT
            )
            G.nodes.append(node)
            yield node

    @staticmethod
    def add_hidden_nodes(i, n, G):
        for c in range(n):
            node = NNode.create_from_nodetype(
                NodeType.NEURON, c + 1 + i, NodePlace.HIDDEN
            )
            G.nodes.append(node)
            yield node

    @staticmethod
    def add_input_nodes(i, G):
        for c in range(i):
            np = NodePlace.INPUT if c + 1 < i else NodePlace.BIAS
            node = NNode.create_from_nodetype(NodeType.SENSOR, c + 1, np)
            G.nodes.append(node)
            yield node

    @staticmethod
    def create_3_possible_types(num_in: int, num_out: int, num_hidden: int, type: int):
        G = Genome()
        inputs: list[NNode] = []
        outputs: list[NNode] = []
        hidden: list[NNode] = []
        bias: NNode | None = None

        node: NNode
        gene: Gene
        trait: Trait

        c: int
        c: int

        G.genome_id = 0

        trait = Trait.create_from_manual(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        G.traits.append(trait)

        num_hidden = type * num_in * num_out

        for c in range(num_in):
            if c + 1 < num_in:
                node = NNode.create_from_nodetype(
                    NodeType.SENSOR, c + 1, NodePlace.INPUT
                )
            else:
                node = NNode.create_from_nodetype(
                    NodeType.SENSOR, c + 1, NodePlace.BIAS
                )
                bias = node
            G.nodes.append(node)
            inputs.append(node)
        for node in Genome.add_hidden_nodes(num_in, num_hidden, G):
            hidden.append(node)

        for c in range(num_out):
            node = NNode.create_from_nodetype(
                NodeType.NEURON, c + num_in + num_hidden + 1, NodePlace.OUTPUT
            )
            G.nodes.append(node)
            outputs.append(node)

        c = 1
        if type == 0:
            for node1 in outputs:
                for node2 in inputs:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, c, 0)

                    G.genes.append(gene)

                    c += 1

        elif type == 1:
            node3 = 0
            for node1 in outputs:
                for node2 in inputs:
                    gene = Gene.create_a_trait(
                        trait, 0, node2, hidden[node3], False, c, 0
                    )
                    G.genes.append(gene)

                    c += 1

                    gene = Gene.create_a_trait(
                        trait, 0, hidden[node3], node1, False, c, 0
                    )
                    G.genes.append(gene)

                    node3 += 1
                    c += 1

        elif type == 2:
            for node1 in hidden:
                for node2 in inputs:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, c, 0)
                    G.genes.append(gene)
                    c += 1

            for node1 in outputs:
                for node2 in hidden:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, c, 0)
                    G.genes.append(gene)
                    c += 1

            for node1 in outputs:
                gene = Gene.create_a_trait(trait, 0, bias, node1, False, c, 0)
                G.genes.append(gene)
                c += 1

            for node1 in hidden:
                for node2 in hidden:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, True, c, 0)
                    G.genes.append(gene)
                    c += 1
        return G

    def get_last_node_id(self) -> int:
        return self.nodes[-1].node_id + 1

    def get_last_gene_innovation_number(self) -> float:
        return self.genes[-1].innovation_num + 1

    def genesis(self, id: int) -> Network:
        new_node: NNode
        trait: Trait | None
        link: Link
        new_link: Link

        max_weight = 0.0
        weight_mag: float

        in_list: list[NNode] = []
        out_list: list[NNode] = []
        all_list: list[NNode] = []

        in_node: NNode
        out_node: NNode

        new_net: Network

        for node in self.nodes:
            new_node = NNode.create_from_nodetype(node.type, node.node_id)

            trait = node.node_trait
            new_node.derive_trait(trait)

            if node.gen_node_label in {NodePlace.INPUT, NodePlace.BIAS}:
                in_list.append(new_node)
            if node.gen_node_label == NodePlace.OUTPUT:
                out_list.append(new_node)

            all_list.append(new_node)

            node.analogue = new_node

        for gene in self.genes:
            if gene.enable:
                link = gene.link

                assert link.in_node is not None
                assert link.out_node is not None

                in_node = link.in_node.analogue
                out_node = link.out_node.analogue
                new_link = Link.create_no_trait(
                    link.weight, in_node, out_node, link.is_recurrent
                )

                out_node.incoming.append(new_link)
                in_node.outgoing.append(new_link)

                trait = link.link_trait

                new_link.derive_trait(trait)

                weight_mag = abs(new_link.weight)
                if weight_mag > max_weight:
                    max_weight = weight_mag

        new_net = Network.create_with_lists(in_list, out_list, all_list, id)

        new_net.genotype = self
        self.phenotype = new_net

        new_net.max_weight = max_weight

        return new_net

    def duplicate(self, new_id: int):
        traits_dup: list[Trait] = []
        nodes_dup: list[NNode] = []
        genes_dup: list[Gene] = []
        new_trait: Trait
        new_node: NNode
        new_gene: Gene
        assoc_trait: Trait | None
        inode: NNode
        out_node: NNode
        trait_ptr: Trait | None
        new_genome: Genome
        for trait in self.traits:
            new_trait = Trait.create_from_one(trait)
            traits_dup.append(new_trait)
        for node in self.nodes:
            if (node.node_trait) == 0:
                assoc_trait = None
            else:
                trait = 0
                assert node.node_trait is not None
                while traits_dup[trait].trait_id != node.node_trait.trait_id:
                    trait += 1
                assoc_trait = traits_dup[trait]

            new_node = NNode.create_from_nnode_and_trait(node, assoc_trait)

            node.dup = new_node
            nodes_dup.append(new_node)

        for gene in self.genes:
            assert gene.link.in_node is not None
            assert gene.link.out_node is not None
            inode = gene.link.in_node.dup
            out_node = gene.link.out_node.dup

            trait_ptr = gene.link.link_trait
            if trait_ptr is None:
                assoc_trait = None
            else:
                trait = 0
                while traits_dup[trait].trait_id != trait_ptr.trait_id:
                    trait += 1
                assoc_trait = traits_dup[trait]

            new_gene = Gene.create_from_gene(gene, assoc_trait, inode, out_node)
            genes_dup.append(new_gene)

        new_genome = Genome.create_full_genome_specs(
            new_id, traits_dup, nodes_dup, genes_dup
        )

        return new_genome

    def verify(self) -> bool:
        for gene in self.genes:
            inode = gene.link.in_node
            out_node = gene.link.out_node

            if inode not in self.nodes or out_node not in self.nodes:
                return False

        last_id = 0
        for node in self.nodes:
            if node.node_id < last_id:
                return False

            last_id = node.node_id

        return True

    def mutate_random_trait(self):
        (t,) = sample(self.traits, 1)
        t.mutate()

    def mutate_link_trait(self, times: int):
        gene_num: int

        for _ in range(times):
            (t,) = sample(self.traits, 1)

            gene_num = randint(0, len(self.genes) - 1)

            the_gene = 0
            the_gene += gene_num

            if not self.genes[the_gene].frozen:
                self.genes[the_gene].link.link_trait = t

    def mutate_node_trait(self, times: int):
        node_num: int

        for _ in range(times):
            (t,) = sample(self.traits, 1)

            node_num = randint(0, len(self.nodes) - 1)

            the_node = 0
            the_node += node_num

            if not self.nodes[the_node].frozen:
                self.nodes[the_node].node_trait = t

    def mutate_link_weights(self, power: float, rate: float, mut_type: Mutator):
        severe = random() > 0.5
        num = 0.0
        gene_total = len(self.genes)
        end_part = gene_total * 0.8
        power_mod = 1.0

        for gene in self.genes:
            if not gene.frozen:
                if severe:
                    gauss_point = 0.3
                    cold_gaussian_point = 0.1
                elif gene_total >= 10 and num > end_part:
                    gauss_point = 0.5
                    cold_gaussian_point = 0.3
                else:
                    gauss_point = 1.0 - rate
                    cold_gaussian_point = 1.0 - rate - (0.1 if random() > 0.5 else 0)

                rand_num = rand_pos_neg() * random() * power * power_mod
                if mut_type == Mutator.GAUSSIAN:
                    rand_choice = random()
                    if rand_choice > gauss_point:
                        gene.link.weight += rand_num
                    elif rand_choice > cold_gaussian_point:
                        gene.link.weight = rand_num
                elif mut_type == Mutator.COLD_GAUSSIAN:
                    gene.link.weight = rand_num

                gene.link.weight = min(8, max(-8, gene.link.weight))

                gene.mutation_num = gene.link.weight

                num += 1.0

    def mutate_toggle_enable(self, times: int):
        gene_num: int

        for _ in range(times):
            gene_num = randint(0, len(self.genes) - 1)

            the_gene = 0
            the_gene += gene_num

            if self.genes[the_gene].enable:
                check_gene = 0
                while (self.genes[check_gene] != self.genes[-1]) and (
                    self.genes[check_gene].link.in_node
                    != self.genes[the_gene].link.in_node
                    or not self.genes[check_gene].enable
                    or self.genes[check_gene].innovation_num
                    == self.genes[the_gene].innovation_num
                ):
                    check_gene += 1

                if self.genes[check_gene] != self.genes[-1]:
                    self.genes[the_gene].enable = False
            else:
                self.genes[the_gene].enable = True

    def mutate_gene_reenable(self):
        gene = 0

        while (self.genes[gene] != self.genes[-1]) and (self.genes[gene].enable):
            gene += 1

        if self.genes[gene] != self.genes[-1] and not self.genes[gene].enable:
            self.genes[gene].enable = True

    def mutate_add_node(
        self, innovations: list[Innovation], node_id: int, cur_innovation: float
    ) -> bool:
        gene_num: int
        in_node: NNode | None
        out_node: NNode | None
        the_link: Link
        done: bool = False
        new_gene1: Gene | None = None
        new_gene2: Gene | None = None
        new_node: NNode | None = None
        trait_ptr: Trait | None
        old_weight: float
        found: bool
        the_gene: int = 0
        try_count = 0
        found = False
        while try_count < 20 and not found:
            gene_num = randint(0, len(self.genes) - 1)

            the_gene = gene_num
            gene = self.genes[the_gene]
            assert gene.link.in_node is not None
            if gene.enable and gene.link.in_node.gen_node_label != NodePlace.BIAS:
                found = True
            try_count += 1

        if not found:
            return False

        self.genes[the_gene].enable = False

        the_link = self.genes[the_gene].link
        old_weight = self.genes[the_gene].link.weight

        in_node = the_link.in_node
        out_node = the_link.out_node

        the_innovation = 0
        while not done:
            assert in_node is not None
            assert out_node is not None
            if the_innovation == len(innovations):
                trait_ptr = the_link.link_trait
                node_id += 1
                new_node = NNode.create_from_nodetype(
                    NodeType.NEURON, node_id, NodePlace.HIDDEN
                )
                new_node.node_trait = self.traits[0]

                new_gene1 = Gene.create_a_trait(
                    trait_ptr,
                    1.0,
                    in_node,
                    new_node,
                    the_link.is_recurrent,
                    cur_innovation,
                    0,
                )
                new_gene2 = Gene.create_a_trait(
                    trait_ptr,
                    old_weight,
                    new_node,
                    out_node,
                    False,
                    cur_innovation + 1,
                    0,
                )
                cur_innovation += 2.0

                assert in_node is not None
                assert out_node is not None
                innovations.append(
                    Innovation.create_innovation(
                        in_node.node_id,
                        out_node.node_id,
                        cur_innovation - 2.0,
                        cur_innovation - 1.0,
                        new_node.node_id,
                        self.genes[the_gene].innovation_num,
                    )
                )

                done = True

            elif (
                innovations[the_innovation].innovation_type == InnovationType.NEW_NODE
                and innovations[the_innovation].node_in_id == in_node.node_id
                and innovations[the_innovation].node_out_id == out_node.node_id
                and innovations[the_innovation].old_innovation_num
                == self.genes[the_gene].innovation_num
            ):
                trait_ptr = the_link.link_trait

                new_node = NNode.create_from_nodetype(
                    NodeType.NEURON,
                    innovations[the_innovation].new_node_id,
                    NodePlace.HIDDEN,
                )
                new_node.node_trait = self.traits[0]

                new_gene1 = Gene.create_a_trait(
                    trait_ptr,
                    1.0,
                    in_node,
                    new_node,
                    the_link.is_recurrent,
                    innovations[the_innovation].innovation_num1,
                    0,
                )
                new_gene2 = Gene.create_a_trait(
                    trait_ptr,
                    old_weight,
                    new_node,
                    out_node,
                    False,
                    innovations[the_innovation].innovation_num2,
                    0,
                )

                done = True
            else:
                the_innovation += 1

        assert new_gene1 is not None
        assert new_gene2 is not None
        assert new_node is not None

        self.add_gene(self.genes, new_gene1)
        self.add_gene(self.genes, new_gene2)
        self.node_insert(self.nodes, new_node)

        return True

    def mutate_add_link(
        self, innovations: list[Innovation], cur_innov: float, tries: int
    ) -> bool:
        node_num_1: int
        node_num_2: int
        try_count: int
        no_dep1: NNode | None = None
        no_dep2: NNode | None = None
        found = False
        recur_flag: int | None = None
        new_gene: Gene | None = None
        trait_num: int
        new_weight: float
        done: bool
        do_recur: bool
        loop_recur: bool
        first_non_sensor: int
        thresh = len(self.nodes) * len(self.nodes)
        count = 0
        try_count = 0
        do_recur = random() < recur_only_prob

        first_non_sensor = 0
        the_node1 = 0
        while self.nodes[the_node1].type == NodeType.SENSOR:
            first_non_sensor += 1
            the_node1 += 1

        if do_recur:
            while try_count < tries:
                loop_recur = random() > 0.5

                node_num_2 = randint(first_non_sensor, len(self.nodes) - 1)
                node_num_1 = (
                    node_num_2 if loop_recur else randint(0, len(self.nodes) - 1)
                )

                the_node1 = node_num_1
                the_node2 = node_num_2

                no_dep1 = self.nodes[the_node1]
                no_dep2 = self.nodes[the_node2]

                the_gene = 0
                while (
                    the_gene != len(self.genes)
                    and no_dep2.type != NodeType.SENSOR
                    and not (
                        self.genes[the_gene].link.in_node == no_dep1
                        and self.genes[the_gene].link.out_node == no_dep2
                        and self.genes[the_gene].link.is_recurrent
                    )
                ):
                    the_gene += 1

                if the_gene != len(self.genes):
                    try_count += 1
                else:
                    count = 0
                    recur_flag = self.phenotype.is_recur(
                        no_dep1.analogue, no_dep2.analogue, count, thresh
                    )

                    if (
                        no_dep1.type == NodePlace.OUTPUT
                        or no_dep2.type == NodePlace.OUTPUT
                    ):
                        recur_flag = True

                    if not recur_flag:
                        try_count += 1
                    else:
                        try_count = tries
                        found = True
        else:
            while try_count < tries:
                node_num_1 = randint(0, len(self.nodes) - 1)
                node_num_2 = randint(first_non_sensor, len(self.nodes) - 1)

                the_node1 = node_num_1
                the_node2 = node_num_2

                no_dep1 = self.nodes[the_node1]
                no_dep2 = self.nodes[the_node2]

                the_gene = 0
                while (
                    the_gene != len(self.genes)
                    and no_dep2.type != NodeType.SENSOR
                    and not (  # Don't allow SENSORS to get input
                        self.genes[the_gene].link.in_node == no_dep1
                        and self.genes[the_gene].link.out_node == no_dep2
                        and not self.genes[the_gene].link.is_recurrent
                    )
                ):
                    the_gene += 1

                if the_gene != len(self.genes):
                    try_count += 1
                else:
                    count = 0
                    recur_flag = self.phenotype.is_recur(
                        no_dep1.analogue, no_dep2.analogue, count, thresh
                    )

                    if (
                        no_dep1.type == NodePlace.OUTPUT
                        or no_dep2.type == NodePlace.OUTPUT
                    ):
                        recur_flag = True

                    if recur_flag:
                        try_count += 1
                    else:
                        try_count = tries
                        found = True

        if not found:
            return False

        the_innov = 0

        if do_recur:
            recur_flag = True

        done = False

        while not done:
            assert no_dep1 is not None
            assert no_dep2 is not None
            if the_innov == len(innovations):
                if self.phenotype == 0:
                    return False

                trait_num = randint(0, len(self.traits) - 1)

                new_weight = rand_pos_neg() * random() * 1.0

                assert recur_flag is not None
                new_gene = Gene.create_a_trait(
                    self.traits[trait_num],
                    new_weight,
                    no_dep1,
                    no_dep2,
                    recur_flag,
                    cur_innov,
                    new_weight,
                )
                innovations.append(
                    Innovation.create_link_innovation(
                        no_dep1.node_id,
                        no_dep2.node_id,
                        cur_innov,
                        new_weight,
                        trait_num,
                    )
                )

                cur_innov = cur_innov + 1.0

                done = True
            elif (
                innovations[the_innov].innovation_type == InnovationType.NEW_LINK
                and innovations[the_innov].node_in_id == no_dep1.node_id
                and innovations[the_innov].node_out_id == no_dep2.node_id
                and innovations[the_innov].recur_flag == recur_flag
            ):
                assert recur_flag is not None
                new_gene = Gene.create_a_trait(
                    self.traits[innovations[the_innov].new_trait_number],
                    innovations[the_innov].new_weight,
                    no_dep1,
                    no_dep2,
                    recur_flag,
                    innovations[the_innov].innovation_num1,
                    0,
                )

                done = True
            else:
                the_innov += 1
        assert new_gene is not None
        self.add_gene(self.genes, new_gene)

        return True

    def mutate_add_sensor(self, innovations: list[Innovation], current_innov: float):
        sensors: list[NNode] = []
        outputs: list[NNode] = []
        node: NNode
        sensor: NNode
        output: NNode
        gene: Gene

        new_weight = 0.0
        new_gene: Gene | None = None

        i: int
        found: bool

        done: bool

        output_connections: int

        trait_num: int

        for i, node in enumerate(self.nodes):
            if node.type == NodeType.SENSOR:
                sensors.append(node)
            elif node.gen_node_label == NodePlace.OUTPUT:
                outputs.append(node)

        for sensor in sensors:
            output_connections = 0

            for gene in self.genes:
                assert gene.link.out_node is not None
                if gene.link.out_node.gen_node_label == NodePlace.OUTPUT:
                    output_connections += 1

            if output_connections == len(outputs):
                sensors.remove(sensor)

        if len(sensors) == 0:
            return

        sensor = sensors[randint(0, len(sensors) - 1)]

        for i, output in enumerate(outputs):
            output = outputs[i]

            found = False
            for gene in self.genes:
                if gene.link.in_node == sensor and gene.link.out_node == output:
                    found = True

            if not found:
                the_innov = 0
                done = False

                while not done:
                    if the_innov == len(innovations):
                        trait_num = randint(0, len(self.traits) - 1)

                        new_weight = rand_pos_neg() * random() * 3.0

                        new_gene = Gene.create_a_trait(
                            self.traits[trait_num],
                            new_weight,
                            sensor,
                            output,
                            False,
                            current_innov,
                            new_weight,
                        )

                        innovations.append(
                            Innovation.create_link_innovation(
                                sensor.node_id,
                                output.node_id,
                                current_innov,
                                new_weight,
                                trait_num,
                            )
                        )

                        current_innov = current_innov + 1.0

                        done = True
                    elif (
                        (
                            (innovations[the_innov]).innovation_type
                            == InnovationType.NEW_LINK
                        )
                        and ((innovations[the_innov]).node_in_id == (sensor.node_id))
                        and ((innovations[the_innov]).node_out_id == (output.node_id))
                        and ((innovations[the_innov]).recur_flag == False)
                    ):
                        new_gene = Gene.create_a_trait(
                            self.traits[innovations[the_innov].new_trait_number],
                            (innovations[the_innov]).new_weight,
                            sensor,
                            output,
                            False,
                            (innovations[the_innov]).innovation_num1,
                            0,
                        )

                        done = True

                    else:
                        the_innov += 1
                assert new_gene is not None
                self.add_gene(self.genes, new_gene)

    def mate_multipoint(
        self,
        g,
        genome_id: int,
        fitness1: float,
        fitness2: float,
    ):
        assert isinstance(g, Genome)
        new_traits: list[Trait] = []
        new_nodes: list[NNode] = []
        new_genes: list[Gene] = []
        new_genome: Genome

        new_trait: Trait

        p1innov: float
        p2innov: float
        chosen_gene: Gene | None = None
        trait_num: int
        inode: NNode | None = None
        out_node: NNode | None = None
        new_inode: NNode
        new_out_node: NNode
        node_trait_num: int

        disable: bool

        disable = False
        new_gene: Gene

        p1better: bool

        skip: bool

        p2trait = 0
        for p1trait in self.traits:
            new_trait = Trait.create_from_two(p1trait, g.traits[p2trait])
            new_traits.append(new_trait)
            p2trait += 1

        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            p1better = len(self.genes) < len(g.genes)
        else:
            p1better = False

        for node in g.nodes:
            if (
                node.gen_node_label == NodePlace.INPUT
                or node.gen_node_label == NodePlace.BIAS
                or node.gen_node_label == NodePlace.OUTPUT
            ):
                node_trait_num = self._get_node_trait_num(node)

                new_out_node = NNode.create_from_nnode_and_trait(
                    node, new_traits[node_trait_num]
                )

                self.node_insert(new_nodes, new_out_node)

        p1gene = 0
        p2gene = 0
        while not (p1gene == len(self.genes) and p2gene == len(g.genes)):
            skip = False

            if p1gene == len(self.genes):
                chosen_gene = g.genes[p2gene]
                p2gene += 1
                if p1better:
                    skip = True
            elif p2gene == len(g.genes):
                chosen_gene = self.genes[p1gene]
                p1gene += 1
                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1gene].innovation_num
                p2innov = g.genes[p2gene].innovation_num

                if p1innov == p2innov:
                    chosen_gene = select_random(self.genes[p1gene], g.genes[p2gene])

                    if (
                        not (self.genes[p1gene].enable and g.genes[p2gene].enable)
                        and random() < 0.75
                    ):
                        disable = True

                    p1gene += 1
                    p2gene += 1
                elif p1innov < p2innov:
                    chosen_gene = self.genes[p1gene]
                    p1gene += 1

                    if not p1better:
                        skip = True
                elif p2innov < p1innov:
                    chosen_gene = g.genes[p2gene]
                    p2gene += 1
                    if p1better:
                        skip = True

            gene2 = 0
            assert chosen_gene is not None
            cgl = chosen_gene.link
            cg2 = new_genes[gene2].link

            assert cg2.in_node is not None
            assert cg2.out_node is not None

            assert cgl.in_node is not None
            assert cgl.out_node is not None

            while gene2 != len(new_genes) and not (
                self.compare_same_nodes(cgl, cg2)
                or self.compare_different_nodes(cgl, cg2)
            ):
                gene2 += 1
                cg2 = new_genes[gene2].link

                assert cg2.in_node is not None
                assert cg2.out_node is not None

            if gene2 != len(new_genes):
                skip = True

            if not skip:
                if chosen_gene.link.link_trait == 0:
                    trait_num = self.traits[0].trait_id - 1
                else:
                    assert chosen_gene.link.link_trait is not None
                    trait_num = (
                        chosen_gene.link.link_trait.trait_id - self.traits[0].trait_id
                    )

                inode = chosen_gene.link.in_node
                out_node = chosen_gene.link.out_node
                assert inode is not None
                assert out_node is not None
                if inode.node_id < out_node.node_id:
                    new_inode = self.while_insert_new_nodes(
                        new_traits, new_nodes, inode
                    )
                    new_out_node = self.while_insert_new_nodes(
                        new_traits, new_nodes, out_node
                    )
                else:
                    new_out_node = self.while_insert_new_nodes(
                        new_traits, new_nodes, out_node
                    )
                    new_inode = self.while_insert_new_nodes(
                        new_traits, new_nodes, inode
                    )

                new_gene = Gene.create_from_gene(
                    chosen_gene, new_traits[trait_num], new_inode, new_out_node
                )
                if disable:
                    new_gene.enable = False
                    disable = False
                new_genes.append(new_gene)

        new_genome = Genome.create_full_genome_specs(
            genome_id, new_traits, new_nodes, new_genes
        )

        return new_genome

    @staticmethod
    def compare_different_nodes(cgl, cg2):
        return (
            cg2.in_node.node_id == cgl.out_node.node_id
            and cg2.out_node.node_id == cgl.in_node.node_id
            and not (cg2.is_recurrent or cgl.is_recurrent)
        )

    @staticmethod
    def compare_same_nodes(cgl, cg2):
        return (
            cg2.in_node.node_id == cgl.in_node.node_id
            and cg2.out_node.node_id == cgl.out_node.node_id
            and cg2.is_recurrent == cgl.is_recurrent
        )

    def while_insert_new_nodes(self, new_traits, new_nodes, inode):
        node = self._while_new_nodes(new_nodes, inode)
        new_inode = self.insert_new_nodes(new_traits, new_nodes, inode, node)

        return new_inode

    def insert_new_nodes(self, new_traits, new_nodes, inode, node):
        if node == len(new_nodes):
            node_trait_num = self._get_node_trait_num(inode)
            new_inode = NNode.create_from_nnode_and_trait(
                inode, new_traits[node_trait_num]
            )
            self.node_insert(new_nodes, new_inode)
        else:
            new_inode = new_nodes[node]
        return new_inode

    def mate_multipoint_avg(
        self,
        g,
        genome_id: int,
        fitness1: float,
        fitness2: float,
    ):
        assert isinstance(g, Genome)
        new_traits: list[Trait] = []
        new_nodes: list[NNode] = []
        new_genes: list[Gene] = []
        new_trait: Trait
        p1innov: float
        p2innov: float
        chosen_gene: Gene | None = None
        trait_num: int
        inode: NNode
        out_node: NNode
        new_inode: NNode
        new_out_node: NNode
        node_trait_num: int
        avg_gene: Gene
        new_gene: Gene
        skip: bool
        p1better: bool

        p2trait = 0
        for p1trait in self.traits:
            new_trait = Trait.create_from_two(p1trait, g.traits[p2trait])
            new_traits.append(new_trait)
            p2trait += 1

        avg_gene = Gene.create_a_trait(None, 0, None, None, False, 0, 0)

        for node in g.nodes:
            if (
                node.gen_node_label == NodePlace.INPUT
                or node.gen_node_label == NodePlace.OUTPUT
                or node.gen_node_label == NodePlace.BIAS
            ):
                node_trait_num = self._get_node_trait_num(node)

                new_out_node = NNode.create_from_nnode_and_trait(
                    node, new_traits[node_trait_num]
                )

                self.node_insert(new_nodes, new_out_node)

        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            p1better = len(self.genes) < len(g.genes)
        else:
            p1better = False

        p1gene = 0
        p2gene = 0
        while not (p1gene == len(self.genes) and p2gene == len(g.genes)):
            avg_gene.enable = True

            skip = False

            if p1gene == len(self.genes):
                chosen_gene = g.genes[p2gene]
                p2gene += 1

                if p1better:
                    skip = True
            elif p2gene == len(g.genes):
                chosen_gene = self.genes[p1gene]
                p1gene += 1

                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1gene].innovation_num
                p2innov = g.genes[p2gene].innovation_num

                if p1innov == p2innov:
                    av = avg_gene.link
                    p1 = self.genes[p1gene].link
                    p2 = self.genes[p2gene].link
                    av.link_trait = select_random(p1, p2).link_trait

                    av.weight = p1.weight + p2.weight / 2.0

                    av.in_node = select_random(p1, p2).in_node
                    av.out_node = select_random(p1, p2).out_node
                    av.is_recurrent = select_random(p1, p2).is_recurrent

                    avg_gene.innovation_num = self.genes[p1gene].innovation_num
                    avg_gene.mutation_num = (
                        self.genes[p1gene].mutation_num + g.genes[p2gene].mutation_num
                    ) / 2.0

                    if not (self.genes[p1gene].enable and g.genes[p2gene].enable):
                        if random() < 0.75:
                            avg_gene.enable = False

                    chosen_gene = avg_gene
                    p1gene += 1
                    p2gene += 1
                elif p1innov < p2innov:
                    chosen_gene = self.genes[p1gene]
                    p1gene += 1

                    if not p1better:
                        skip = True
                elif p2innov < p1innov:
                    chosen_gene = g.genes[p2gene]
                    p2gene += 1

                    if p1better:
                        skip = True

            gene2 = 0
            assert chosen_gene is not None
            cg = chosen_gene.link
            assert cg.in_node is not None
            assert cg.out_node is not None
            while gene2 != len(new_genes):
                cg2 = new_genes[gene2].link
                assert cg2.in_node is not None
                assert cg2.out_node is not None
                if (
                    cg2.in_node.node_id == cg.in_node.node_id
                    and cg2.out_node.node_id == cg.out_node.node_id
                    and cg2.is_recurrent == cg.is_recurrent
                ) or (
                    cg2.out_node.node_id == cg.in_node.node_id
                    and cg2.in_node.node_id == cg.out_node.node_id
                    and not (cg2.is_recurrent or cg.is_recurrent)
                ):
                    skip = True
                gene2 += 1

            if not skip:
                trait_num = self._get_trait_num(cg)
                inode = cg.in_node
                out_node = cg.out_node

                if inode.node_id < out_node.node_id:
                    node = self._while_new_nodes(new_nodes, inode)

                    if node == len(new_nodes):
                        node_trait_num = self._get_node_trait_num(inode)
                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, new_traits[node_trait_num]
                        )

                        self.node_insert(new_nodes, new_inode)
                    else:
                        new_inode = new_nodes[node]

                    node = self._while_new_nodes(new_nodes, out_node)
                    if node == len(new_nodes):
                        node_trait_num = self._get_node_trait_num(out_node)
                        new_out_node = NNode.create_from_nnode_and_trait(
                            out_node, new_traits[node_trait_num]
                        )

                        self.node_insert(new_nodes, new_out_node)
                    else:
                        new_out_node = new_nodes[node]
                else:
                    node = self._while_new_nodes(new_nodes, out_node)
                    if node == len(new_nodes):
                        node_trait_num = self._get_node_trait_num(out_node)
                        new_out_node = NNode.create_from_nnode_and_trait(
                            out_node, new_traits[node_trait_num]
                        )

                        self.node_insert(new_nodes, new_out_node)
                    else:
                        new_out_node = new_nodes[node]

                    node = self._while_new_nodes(new_nodes, inode)
                    if node == len(new_nodes):
                        node_trait_num = self._get_node_trait_num(inode)

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, new_traits[node_trait_num]
                        )

                        self.node_insert(new_nodes, new_inode)
                    else:
                        new_inode = new_nodes[node]

                new_gene = Gene.create_from_gene(
                    chosen_gene, new_traits[trait_num], new_inode, new_out_node
                )

                new_genes.append(new_gene)

        del avg_gene

        return Genome.create_full_genome_specs(
            genome_id, new_traits, new_nodes, new_genes
        )

    @staticmethod
    def _while_new_nodes(nodes, node):
        counter = 0
        while counter != len(nodes) and nodes[counter].node_id != node.node_id:
            counter += 1
        return counter

    def _get_trait_num(self, cg):
        if cg.link_trait is None:
            trait_num = self.traits[0].trait_id - 1
        else:
            trait_num = cg.link_trait.trait_id - self.traits[0].trait_id
        return trait_num

    def _get_node_trait_num(self, node):
        if not node.node_trait:
            node_trait_num = 0
        else:
            node_trait_num = node.node_trait.trait_id - self.traits[0].trait_id
        return node_trait_num

    def mate_singlepoint(self, g, genome_id: int):
        assert isinstance(g, Genome)
        new_traits: list[Trait] = []
        new_nodes: list[NNode] = []
        new_genes: list[Gene] = []

        new_trait: Trait

        p1innov: float  # Innovation numbers for genes inside parents' Genomes
        p2innov: float
        chosen_gene: Gene | None = None  # Gene chosen for baby to inherit
        trait_num: int  # Number of trait new gene points to
        inode: NNode  # NNodes connected to the chosen Gene
        out_node: NNode
        new_inode: NNode
        new_out_node: NNode

        avg_gene: Gene

        cross_point: int  # The point in the Genome to cross at
        gene_counter: int  # Counts up to the cross_point
        skip: bool  # Used for skipping unwanted genes

        p2trait = 0
        for p1trait in self.traits:
            # Construct by averaging
            new_trait = Trait.create_from_two(p1trait, g.traits[p2trait])
            new_traits.append(new_trait)
            p2trait += 1

        avg_gene = Gene.create_a_trait(None, 0, None, None, False, 0, 0)

        if len(self.genes) < len(g.genes):
            s = self.genes
            o = g.genes
            cross_point = randint(0, len(self.genes) - 1)
            p1gene = 0
            p2gene = 0
            stopper = len(g.genes)
            p1stop = len(self.genes)
            p2stop = len(g.genes)
        else:
            s = g.genes
            o = self.genes
            cross_point = randint(0, len(g.genes) - 1)
            p2gene = 0
            p1gene = 0
            stopper = len(self.genes)
            p1stop = len(g.genes)
            p2stop = len(self.genes)

        gene_counter = 0  # Ready to count to cross_point

        skip = False  # Default to not skip a Gene

        while p2gene != stopper:
            avg_gene.enable = True  # Default to True

            if p1gene == p1stop:
                chosen_gene = o[p2gene]
                p2gene += 1
            elif p2gene == p2stop:
                chosen_gene = s[p1gene]
                p1gene += 1
            else:
                p1innov = s[p1gene].innovation_num
                p2innov = o[p2gene].innovation_num

                if p1innov == p2innov:
                    if gene_counter < cross_point:
                        chosen_gene = s[p1gene]
                    elif gene_counter > cross_point:
                        chosen_gene = o[p2gene]
                    else:
                        avg_gene.link.link_trait = select_random(
                            s[p1gene], o[p2gene]
                        ).link.link_trait

                        avg_gene.link.weight = (
                            s[p1gene].link.weight + o[p2gene].link.weight
                        ) / 2.0

                        avg_gene.link.in_node = select_random(
                            s[p1gene], o[p2gene]
                        ).link.in_node
                        avg_gene.link.out_node = select_random(
                            s[p1gene], o[p2gene]
                        ).link.out_node
                        avg_gene.link.is_recurrent = select_random(
                            s[p1gene], o[p2gene]
                        ).link.is_recurrent

                        avg_gene.innovation_num = s[p1gene].innovation_num
                        avg_gene.mutation_num = (
                            s[p1gene].mutation_num + o[p2gene].mutation_num
                        ) / 2.0

                        if not (s[p1gene].enable and o[p2gene].enable):
                            avg_gene.enable = False

                        chosen_gene = avg_gene

                    p1gene += 1
                    p2gene += 1
                    gene_counter += 1
                elif p1innov < p2innov:
                    if gene_counter < cross_point:
                        chosen_gene = s[p1gene]
                        p1gene += 1
                        gene_counter += 1
                    else:
                        chosen_gene = o[p2gene]
                        p2gene += 1
                elif p2innov < p1innov:
                    p2gene += 1
                    skip = True  # Special case: we need to skip to the next iteration

            gene2 = 0

            ng2 = new_genes[gene2].link
            assert chosen_gene is not None
            cg = chosen_gene.link
            assert ng2.in_node is not None
            assert ng2.out_node is not None
            assert cg.in_node is not None
            assert cg.out_node is not None
            while gene2 != len(new_genes) and not (
                Genome.compare_same_nodes(ng2, cg)
                or Genome.compare_different_nodes(ng2, cg)
            ):
                gene2 += 1

            if gene2 != len(new_genes):
                skip = True  # Link is a duplicate

            if not skip:
                trait_num = self._get_trait_num(cg)

                inode = cg.in_node
                out_node = cg.out_node

                if inode.node_id < out_node.node_id:
                    new_inode = self.while_insert_new_nodes(
                        new_traits, new_nodes, inode
                    )
                    new_out_node = self.while_insert_new_nodes(
                        new_traits, new_nodes, out_node
                    )
                else:
                    new_out_node = self.while_insert_new_nodes(
                        new_traits, new_nodes, out_node
                    )
                    new_inode = self.while_insert_new_nodes(
                        new_traits, new_nodes, inode
                    )

                new_gene = Gene.create_from_gene(
                    chosen_gene, new_traits[trait_num], new_inode, new_out_node
                )
                new_genes.append(new_gene)

            skip = False

        del avg_gene  # Clean up used object

        return Genome.create_full_genome_specs(
            genome_id, new_traits, new_nodes, new_genes
        )

    def compatibility(self, g) -> float:
        assert isinstance(g, Genome)

        p1innov: float
        p2innov: float

        mut_diff: float

        num_disjoint = 0.0
        num_excess = 0.0
        mut_diff_total = 0.0
        num_matching = 0.0

        p1gene = 0
        p2gene = 0
        while not (p1gene == len(self.genes) and p2gene == len(g.genes)):
            if p1gene == len(self.genes):
                p2gene += 1
                num_excess += 1.0
            elif p2gene == len(g.genes):
                p1gene += 1
                num_excess += 1.0
            else:
                p1innov = self.genes[p1gene].innovation_num
                p2innov = g.genes[p2gene].innovation_num

                if p1innov == p2innov:
                    num_matching += 1.0
                    mut_diff = (self.genes[p1gene].mutation_num) - (
                        g.genes[p2gene].mutation_num
                    )
                    if mut_diff < 0.0:
                        mut_diff = 0.0 - mut_diff
                    mut_diff_total += mut_diff

                    p1gene += 1
                    p2gene += 1
                elif p1innov < p2innov:
                    p1gene += 1
                    num_disjoint += 1.0
                elif p2innov < p1innov:
                    p2gene += 1
                    num_disjoint += 1.0

        return (
            disjoint_coefficient * (num_disjoint / 1.0)
            + excess_coefficient * (num_excess / 1.0)
            + mutation_diff_coefficient * (mut_diff_total / num_matching)
        )

    def trait_compare(self, t1: Trait, t2: Trait) -> float:
        id1 = t1.trait_id
        id2 = t2.trait_id

        if id1 == 1 and id2 >= 2 or id2 == 1 and id1 >= 2:
            return 0.5
        if id1 < 2:
            return 0.0

        params_diff = 0.0
        for count in range(3):
            params_diff += abs(t1.params[count] - t2.params[count])
        return params_diff / 4.0

    def extrons(self) -> int:
        return len([g for g in self.genes if g.enable])

    def randomize_traits(self):
        num_traits = len(self.traits)
        trait_num: int

        for node in self.nodes:
            trait_num = randint(1, num_traits)
            node.trait_id = trait_num

            trait = self._find_new_trait_num(trait_num)
            node.node_trait = self.traits[trait]

        for gene in self.genes:
            trait_num = randint(1, num_traits)
            gene.link.trait_id = trait_num

            trait = self._find_new_trait_num(trait_num)
            gene.link.link_trait = self.traits[trait]

    def _find_new_trait_num(self, trait_num):
        trait = 0
        while self.traits[trait].trait_id != trait_num:
            trait += 1
        return trait

    def node_insert(self, n_list: list[NNode], n: NNode):
        n_id = n.node_id
        node = 0
        while n_list[node] != n_list[-1] and (n_list[node].node_id < n_id):
            node += 1

        n_list.insert(node, n)

    def add_gene(self, gene_list: list[Gene], g: Gene):
        innovation_num = g.innovation_num

        gene = 0
        while (
            gene_list[gene] != gene_list[-1]
            and gene_list[gene].innovation_num < innovation_num
        ):
            gene += 1

        gene_list.insert(gene, g)
