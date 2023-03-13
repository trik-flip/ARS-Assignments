from random import random, randint
from gene import Gene
from nnode import NNode
from trait import Trait
from innovation import Innovation, InnovationType
from network import Network
from enum import Enum
from nnode import NodePlace, NodeType
from link import Link
from week4.src.NEAT.neat import rand_pos_neg
from week4.src.NEAT.util import select_random

disjoint_coeff = 0.5
excess_coeff = 0.5
mutdiff_coeff = 0.5
recur_only_prob = 0.3


class Mutator(Enum):
    GAUSSIAN = 0
    COLDGAUSSIAN = 1


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
        # std::vector<Link *>::iterator curlink;
        gen = Genome()
        gen.traits = t
        gen.nodes = n
        gen.genome_id = id

        # We go through the links and turn them into original genes
        for curlink in links:
            # Create genes one at a time
            tempgene = Gene.create_a_trait(
                curlink.link_trait,
                curlink.weight,
                curlink.in_node,
                curlink.out_node,
                curlink.is_recurrent,
                1.0,
                0.0,
            )
            gen.genes.append(tempgene)

    # This special constructor creates a Genome
    # with i inputs, o outputs, n out of nmax hidden units, and random
    # connectivity.  If r is True then recurrent connections will
    # be included.
    @staticmethod
    # TODO
    def create_special(
        new_id: int, i: int, o: int, n: int, nmax: int, r: bool, linkprob: float
    ):
        G = Genome()
        totalnodes: int
        cm_ptr: int
        matrixdim: int
        count: int
        ncount: int
        row: int
        col: int
        new_weight: float
        max_node: int
        first_output: int
        totalnodes = i + o + nmax
        matrixdim = totalnodes * totalnodes
        cm: list[bool] = []
        max_node = i + n
        first_output = totalnodes - o + 1
        newnode: NNode
        new_gene: Gene
        newtrait: Trait
        in_node: NNode
        out_node: NNode
        genome_id = new_id
        cm_ptr = 0
        for count in range(matrixdim):
            if random() < linkprob:
                cm[cm_ptr] = True
            else:
                cm[cm_ptr] = False
            cm_ptr += 1

        newtrait = Trait.create_from_manual(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        G.traits.append(newtrait)

        for ncount in range(i):
            if ncount + 1 < i:
                np = NodePlace.INPUT
            else:
                np = NodePlace.BIAS
            newnode = NNode.create_from_nodetype(NodeType.SENSOR, ncount + 1, np)

            newnode.node_trait = newtrait

            G.nodes.append(newnode)

        for ncount in range(n):
            newnode = NNode.create_from_nodetype(
                NodeType.NEURON, ncount + 1 + i, NodePlace.HIDDEN
            )
            newnode.node_trait = newtrait
            G.nodes.append(newnode)

        for ncount in range(totalnodes - (first_output - 1)):
            newnode = NNode.create_from_nodetype(
                NodeType.NEURON, ncount + first_output + 1, NodePlace.OUTPUT
            )
            newnode.node_trait = newtrait
            G.nodes.append(newnode)

        ccount = 1

        cm_ptr = 0
        count = 0
        for col in range(1, 1 + totalnodes):
            for row in range(1, totalnodes + 1):
                if (
                    cm[cm_ptr]
                    and col > i
                    and (col <= max_node or col >= first_output)
                    and (row <= max_node or row >= first_output)
                ):
                    node_iter = 0
                    while (G.nodes[node_iter]).node_id != row:
                        node_iter += 1
                    in_node = G.nodes[node_iter]
                    node_iter = 0
                    while (G.nodes[node_iter]).node_id != col:
                        node_iter += 1
                    out_node = G.nodes[node_iter]
                    new_weight = rand_pos_neg() * random()
                    if col > row:
                        new_gene = Gene.create_a_trait(
                            newtrait,
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
                            newtrait,
                            new_weight,
                            in_node,
                            out_node,
                            True,
                            count,
                            new_weight,
                        )

                        G.genes.append(new_gene)

                count += 1
                cm_ptr += 1
        return G

    @staticmethod
    # TODO
    def create_3_possible_types(num_in: int, num_out: int, num_hidden: int, type: int):
        G = Genome()
        inputs: list[NNode] = []
        outputs: list[NNode] = []
        hidden: list[NNode] = []
        bias: NNode

        newnode: NNode
        gene: Gene
        trait: Trait

        count: int
        ncount: int

        G.genome_id = 0

        trait = Trait.create_from_manual(1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        G.traits.append(trait)

        num_hidden = type * num_in * num_out

        for ncount in range(num_in):
            if ncount + 1 < num_in:
                newnode = NNode.create_from_nodetype(
                    NodeType.SENSOR, ncount + 1, NodePlace.INPUT
                )
            else:
                newnode = NNode.create_from_nodetype(
                    NodeType.SENSOR, ncount + 1, NodePlace.BIAS
                )
                bias = newnode

            G.nodes.append(newnode)
            inputs.append(newnode)

        for ncount in range(num_hidden):
            newnode = NNode.create_from_nodetype(
                NodeType.NEURON, ncount + num_in + 1, NodePlace.HIDDEN
            )
            G.nodes.append(newnode)
            hidden.append(newnode)

        for ncount in range(num_out):
            newnode = NNode.create_from_nodetype(
                NodeType.NEURON, ncount + num_in + num_hidden + 1, NodePlace.OUTPUT
            )
            G.nodes.append(newnode)
            outputs.append(newnode)

        count = 1
        if type == 0:
            for node1 in outputs:
                for node2 in inputs:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, count, 0)

                    G.genes.append(gene)

                    count += 1

        elif type == 1:
            node3 = 0
            for node1 in outputs:
                for node2 in inputs:
                    gene = Gene.create_a_trait(
                        trait, 0, node2, hidden[node3], False, count, 0
                    )
                    G.genes.append(gene)

                    count += 1

                    gene = Gene.create_a_trait(
                        trait, 0, hidden[node3], node1, False, count, 0
                    )
                    G.genes.append(gene)

                    node3 += 1
                    count += 1

        elif type == 2:
            for node1 in hidden:
                for node2 in inputs:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, count, 0)

                    G.genes.append(gene)

                    count += 1

            for node1 in outputs:
                for node2 in hidden:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, False, count, 0)

                    G.genes.append(gene)

                    count += 1

            for node1 in outputs:
                gene = Gene.create_a_trait(trait, 0, bias, node1, False, count, 0)

                G.genes.append(gene)

                count += 1

            for node1 in hidden:
                for node2 in hidden:
                    gene = Gene.create_a_trait(trait, 0, node2, node1, True, count, 0)

                    G.genes.append(gene)

                    count += 1
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

        inode: NNode
        onode: NNode

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
                link = gene.lnk
                inode = link.in_node.analogue
                onode = link.out_node.analogue
                new_link = Link.create_no_trait(
                    link.weight, inode, onode, link.is_recurrent
                )

                onode.incoming.append(new_link)
                inode.outgoing.append(new_link)

                trait = link.link_trait

                new_link.derive_trait(trait)

                if new_link.weight > 0:
                    weight_mag = new_link.weight
                else:
                    weight_mag = -new_link.weight
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
        onode: NNode
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
            inode = gene.lnk.in_node.dup
            onode = gene.lnk.out_node.dup

            trait_ptr = gene.lnk.link_trait
            if trait_ptr is None:
                assoc_trait = None
            else:
                trait = 0
                while traits_dup[trait].trait_id != trait_ptr.trait_id:
                    trait += 1
                assoc_trait = traits_dup[trait]

            new_gene = Gene.create_from_gene(gene, assoc_trait, inode, onode)
            genes_dup.append(new_gene)

        new_genome = Genome.create_full_genome_specs(
            new_id, traits_dup, nodes_dup, genes_dup
        )

        return new_genome

    def verify(self) -> bool:
        for gene in self.genes:
            inode = gene.lnk.in_node
            onode = gene.lnk.out_node

            if inode not in self.nodes or onode not in self.nodes:
                return False

        last_id = 0
        for node in self.nodes:
            if node.node_id < last_id:
                return False

            last_id = node.node_id

        return True

    def mutate_random_trait(self):
        traitnum = randint(0, len(self.traits) - 1)
        self.traits[traitnum].mutate()

    def mutate_link_trait(self, times: int):
        gene_num: int

        for _ in range(times):
            trait_num = randint(0, len(self.traits) - 1)

            gene_num = randint(0, len(self.genes) - 1)

            the_gene = 0
            the_gene += gene_num

            if not self.genes[the_gene].frozen:
                self.genes[the_gene].lnk.link_trait = self.traits[trait_num]

    def mutate_node_trait(self, times: int):
        trait_num: int
        node_num: int

        for _ in range(times):
            trait_num = randint(0, (len(self.traits)) - 1)

            node_num = randint(0, len(self.nodes) - 1)

            the_node = 0
            the_node += node_num

            if not (self.nodes[the_node].frozen):
                self.nodes[the_node].node_trait = self.traits[trait_num]

    def mutate_link_weights(self, power: float, rate: float, mut_type: Mutator):
        severe = random() > 0.5
        num = 0.0
        gene_total = len(self.genes)
        endpart = gene_total * 0.8
        powermod = 1.0

        for gene in self.genes:
            if not gene.frozen:
                if severe:
                    gauss_point = 0.3
                    coldgauss_point = 0.1
                elif gene_total >= 10 and num > endpart:
                    gauss_point = 0.5
                    coldgauss_point = 0.3
                else:
                    gauss_point = 1.0 - rate
                    if random() > 0.5:
                        coldgauss_point = 1.0 - rate - 0.1
                    else:
                        coldgauss_point = 1.0 - rate

                rand_num = rand_pos_neg() * random() * power * powermod
                if mut_type == Mutator.GAUSSIAN:
                    rand_choice = random()
                    if rand_choice > gauss_point:
                        gene.lnk.weight += rand_num
                    elif rand_choice > coldgauss_point:
                        gene.lnk.weight = rand_num
                elif mut_type == Mutator.COLDGAUSSIAN:
                    gene.lnk.weight = rand_num

                if gene.lnk.weight > 8.0:
                    gene.lnk.weight = 8.0
                elif gene.lnk.weight < -8.0:
                    gene.lnk.weight = -8.0

                gene.mutation_num = gene.lnk.weight

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
                    self.genes[check_gene].lnk.in_node
                    != self.genes[the_gene].lnk.in_node
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
        self, innovations: list[Innovation], curnode_id: int, cur_innovation: float
    ) -> bool:
        genenum: int
        in_node: NNode
        out_node: NNode
        the_link: Link
        done: bool = False
        new_gene1: Gene
        new_gene2: Gene
        new_node: NNode
        trait_ptr: Trait | None
        old_weight: float
        found: bool
        thegene: int = 0
        trycount = 0
        found = False
        while trycount < 20 and not found:
            genenum = randint(0, len(self.genes) - 1)

            thegene = genenum
            if (
                self.genes[thegene].enable
                and self.genes[thegene].lnk.in_node.gen_node_label != NodePlace.BIAS
            ):
                found = True
            trycount += 1

        if not found:
            return False

        self.genes[thegene].enable = False

        the_link = self.genes[thegene].lnk
        old_weight = self.genes[thegene].lnk.weight

        in_node = the_link.in_node
        out_node = the_link.out_node

        the_innovation = 0

        while not done:
            if the_innovation == len(innovations):
                trait_ptr = the_link.link_trait
                curnode_id += 1
                new_node = NNode.create_from_nodetype(
                    NodeType.NEURON, curnode_id, NodePlace.HIDDEN
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

                innovations.append(
                    Innovation.create_innovation(
                        in_node.node_id,
                        out_node.node_id,
                        cur_innovation - 2.0,
                        cur_innovation - 1.0,
                        new_node.node_id,
                        self.genes[thegene].innovation_num,
                    )
                )

                done = True

            elif (
                (
                    (innovations[the_innovation]).innovation_type
                    == InnovationType.NEW_NODE
                )
                and ((innovations[the_innovation]).node_in_id == (in_node.node_id))
                and ((innovations[the_innovation]).node_out_id == (out_node.node_id))
                and (
                    (innovations[the_innovation]).old_innovation_num
                    == self.genes[thegene].innovation_num
                )
            ):
                trait_ptr = the_link.link_trait

                new_node = NNode.create_from_nodetype(
                    NodeType.NEURON,
                    (innovations[the_innovation]).new_node_id,
                    NodePlace.HIDDEN,
                )
                new_node.node_trait = self.traits[0]

                new_gene1 = Gene.create_a_trait(
                    trait_ptr,
                    1.0,
                    in_node,
                    new_node,
                    the_link.is_recurrent,
                    (innovations[the_innovation]).innovation_num1,
                    0,
                )
                new_gene2 = Gene.create_a_trait(
                    trait_ptr,
                    old_weight,
                    new_node,
                    out_node,
                    False,
                    (innovations[the_innovation]).innovation_num2,
                    0,
                )

                done = True
            else:
                the_innovation += 1

        self.add_gene(self.genes, new_gene1)
        self.add_gene(self.genes, new_gene2)
        self.node_insert(self.nodes, new_node)

        return True

    def mutate_add_link(
        self, innovs: list[Innovation], cur_innov: float, tries: int
    ) -> bool:
        node_num_1: int
        node_num_2: int
        try_count: int
        no_dep1: NNode
        no_dep2: NNode
        found = False
        recur_flag: int
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

                if loop_recur:
                    node_num_1 = randint(first_non_sensor, len(self.nodes) - 1)
                    node_num_2 = node_num_1
                else:
                    node_num_1 = randint(0, len(self.nodes) - 1)
                    node_num_2 = randint(first_non_sensor, len(self.nodes) - 1)

                the_node1 = node_num_1

                the_node2 = node_num_2

                no_dep1 = self.nodes[the_node1]
                no_dep2 = self.nodes[the_node2]

                thegene = 0
                while (
                    thegene != len(self.genes)
                    and no_dep2.type != NodeType.SENSOR
                    and not (
                        self.genes[thegene].lnk.in_node == no_dep1
                        and self.genes[thegene].lnk.out_node == no_dep2
                        and self.genes[thegene].lnk.is_recurrent
                    )
                ):
                    thegene += 1

                if thegene != len(self.genes):
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

                thegene = 0
                while (
                    thegene != len(self.genes)
                    and no_dep2.type != NodeType.SENSOR
                    and not (  # Don't allow SENSORS to get input
                        self.genes[thegene].lnk.in_node == no_dep1
                        and self.genes[thegene].lnk.out_node == no_dep2
                        and not self.genes[thegene].lnk.is_recurrent
                    )
                ):
                    thegene += 1

                if thegene != len(self.genes):
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
            recur_flag = 1

        done = False

        while not done:
            if the_innov == len(innovs):
                if self.phenotype == 0:
                    return False

                trait_num = randint(0, len(self.traits) - 1)

                new_weight = rand_pos_neg() * random() * 1.0

                new_gene = Gene.create_a_trait(
                    self.traits[trait_num],
                    new_weight,
                    no_dep1,
                    no_dep2,
                    recur_flag,
                    cur_innov,
                    new_weight,
                )

                innovs.append(
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
                innovs[the_innov].innovation_type == InnovationType.NEW_LINK
                and innovs[the_innov].node_in_id == no_dep1.node_id
                and innovs[the_innov].node_out_id == no_dep2.node_id
                and innovs[the_innov].recur_flag == recur_flag
            ):
                new_gene = Gene.create_a_trait(
                    self.traits[innovs[the_innov].new_trait_number],
                    innovs[the_innov].new_weight,
                    no_dep1,
                    no_dep2,
                    recur_flag,
                    innovs[the_innov].innovation_num1,
                    0,
                )

                done = True
            else:
                the_innov += 1
        assert new_gene is not None
        self.add_gene(self.genes, new_gene)

        return True

    def mutate_add_sensor(self, innovs: list[Innovation], curinnov: float):
        sensors: list[NNode] = []
        outputs: list[NNode] = []
        node: NNode
        sensor: NNode
        output: NNode
        gene: Gene

        newweight = 0.0
        newgene: Gene | None = None

        i: int
        found: bool

        done: bool

        outputConnections: int

        traitnum: int

        for i, node in enumerate(self.nodes):
            if node.type == NodeType.SENSOR:
                sensors.append(node)
            elif node.gen_node_label == NodePlace.OUTPUT:
                outputs.append(node)

        for sensor in sensors:
            outputConnections = 0

            for gene in self.genes:
                if gene.lnk.out_node.gen_node_label == NodePlace.OUTPUT:
                    outputConnections += 1

            if outputConnections == len(outputs):
                iter = sensors.remove(sensor)

        if len(sensors) == 0:
            return

        sensor = sensors[randint(0, len(sensors) - 1)]

        for i, output in enumerate(outputs):
            output = outputs[i]

            found = False
            for j, gene in enumerate(self.genes):
                if gene.lnk.in_node == sensor and gene.lnk.out_node == output:
                    found = True

            if not found:
                theinnov = 0
                done = False

                while not done:
                    if theinnov == len(innovs):
                        traitnum = randint(0, len(self.traits) - 1)
                        thetrait = 0

                        newweight = rand_pos_neg() * random() * 3.0

                        newgene = Gene.create_a_trait(
                            self.traits[traitnum],
                            newweight,
                            sensor,
                            output,
                            False,
                            curinnov,
                            newweight,
                        )

                        innovs.append(
                            Innovation.create_link_innovation(
                                sensor.node_id,
                                output.node_id,
                                curinnov,
                                newweight,
                                traitnum,
                            )
                        )

                        curinnov = curinnov + 1.0

                        done = True
                    elif (
                        ((innovs[theinnov]).innovation_type == InnovationType.NEW_LINK)
                        and ((innovs[theinnov]).node_in_id == (sensor.node_id))
                        and ((innovs[theinnov]).node_out_id == (output.node_id))
                        and ((innovs[theinnov]).recur_flag == False)
                    ):
                        newgene = Gene.create_a_trait(
                            self.traits[innovs[theinnov].new_trait_number],
                            (innovs[theinnov]).new_weight,
                            sensor,
                            output,
                            False,
                            (innovs[theinnov]).innovation_num1,
                            0,
                        )

                        done = True

                    else:
                        theinnov += 1
                assert newgene is not None
                self.add_gene(self.genes, newgene)

    def mate_multipoint(
        self,
        g,
        genomeid: int,
        fitness1: float,
        fitness2: float,
        interspec_flag: bool,
    ):
        assert isinstance(g, Genome)
        newtraits: list[Trait] = []
        newnodes: list[NNode] = []
        newgenes: list[Gene] = []
        new_genome: Genome

        newtrait: Trait

        p1innov: float
        p2innov: float
        chosengene: Gene
        traitnum: int
        inode: NNode
        onode: NNode
        new_inode: NNode
        new_onode: NNode
        nodetraitnum: int

        disable: bool

        disable = False
        newgene: Gene

        p1better: bool

        skip: bool

        p2trait = 0
        for p1trait in self.traits:
            newtrait = Trait.create_from_two(p1trait, g.traits[p2trait])
            newtraits.append(newtrait)
            p2trait += 1

        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            p1better = len(self.genes) < len(g.genes)
        else:
            p1better = False

        for curnode in g.nodes:
            if (
                curnode.gen_node_label == NodePlace.INPUT
                or curnode.gen_node_label == NodePlace.BIAS
                or curnode.gen_node_label == NodePlace.OUTPUT
            ):
                if not curnode.node_trait:
                    nodetraitnum = 0
                else:
                    nodetraitnum = curnode.node_trait.trait_id - self.traits[0].trait_id

                new_onode = NNode.create_from_nnode_and_trait(
                    curnode, newtraits[nodetraitnum]
                )

                self.node_insert(newnodes, new_onode)

        p1gene = 0
        p2gene = 0
        while not ((p1gene == len(self.genes)) and (p2gene == len(g.genes))):
            skip = False

            if p1gene == len(self.genes):
                chosengene = g.genes[p2gene]
                p2gene += 1
                if p1better:
                    skip = True
            elif p2gene == len(g.genes):
                chosengene = self.genes[p1gene]
                p1gene += 1
                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1gene].innovation_num
                p2innov = g.genes[p2gene].innovation_num

                if p1innov == p2innov:
                    chosengene = select_random(self.genes[p1gene], g.genes[p2gene])

                    if (
                        not (self.genes[p1gene].enable and g.genes[p2gene].enable)
                        and random() < 0.75
                    ):
                        disable = True

                    p1gene += 1
                    p2gene += 1
                elif p1innov < p2innov:
                    chosengene = self.genes[p1gene]
                    p1gene += 1

                    if not p1better:
                        skip = True
                elif p2innov < p1innov:
                    chosengene = g.genes[p2gene]
                    p2gene += 1
                    if p1better:
                        skip = True

            curgene2 = 0
            cgl = chosengene.lnk
            cg2 = newgenes[curgene2].lnk
            while (curgene2 != len(newgenes)) and not (
                (
                    cg2.in_node.node_id == cgl.in_node.node_id
                    and cg2.out_node.node_id == cgl.out_node.node_id
                    and cg2.is_recurrent == cgl.is_recurrent
                )
                or (
                    cg2.in_node.node_id == cgl.out_node.node_id
                    and (cg2.out_node.node_id == cgl.in_node.node_id)
                    and not (cg2.is_recurrent or cgl.is_recurrent)
                )
            ):
                curgene2 += 1
                cg2 = newgenes[curgene2].lnk

            if curgene2 != len(newgenes):
                skip = True

            if not skip:
                if chosengene.lnk.link_trait == 0:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = (
                        chosengene.lnk.link_trait.trait_id - self.traits[0].trait_id
                    )

                inode = chosengene.lnk.in_node
                onode = chosengene.lnk.out_node

                if inode.node_id < onode.node_id:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1

                    if curnode == len(newnodes):
                        if not (inode.node_trait):
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                inode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not (onode.node_trait):
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                onode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]
                else:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not (onode.node_trait):
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                onode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]

                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not inode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                inode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                newgene = Gene.create_from_gene(
                    chosengene, newtraits[traitnum], new_inode, new_onode
                )
                if disable:
                    newgene.enable = False
                    disable = False
                newgenes.append(newgene)

        new_genome = Genome.create_full_genome_specs(
            genomeid, newtraits, newnodes, newgenes
        )

        return new_genome

    def mate_multipoint_avg(
        self,
        g,
        genomeid: int,
        fitness1: float,
        fitness2: float,
        interspec_flag: bool,
    ):
        assert isinstance(g, Genome)
        newtraits: list[Trait] = []
        newnodes: list[NNode] = []
        newgenes: list[Gene] = []

        newtrait: Trait

        p1innov: float
        p2innov: float
        chosengene: Gene
        traitnum: int
        inode: NNode
        onode: NNode
        new_inode: NNode
        new_onode: NNode

        nodetraitnum: int

        avgene: Gene

        newgene: Gene

        skip: bool

        p1better: bool

        p2trait = 0
        for p1trait in self.traits:
            newtrait = Trait.create_from_two(p1trait, g.traits[p2trait])
            newtraits.append(newtrait)
            p2trait += 1

        avgene = Gene.create_a_trait(None, 0, 0, 0, 0, 0, 0)

        for curnode in g.nodes:
            if (
                curnode.gen_node_label == NodePlace.INPUT
                or curnode.gen_node_label == NodePlace.OUTPUT
                or curnode.gen_node_label == NodePlace.BIAS
            ):
                if not curnode.node_trait:
                    nodetraitnum = 0
                else:
                    nodetraitnum = curnode.node_trait.trait_id - self.traits[0].trait_id

                new_onode = NNode.create_from_nnode_and_trait(
                    curnode, newtraits[nodetraitnum]
                )

                self.node_insert(newnodes, new_onode)

        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            p1better = len(self.genes) < len(g.genes)
        else:
            p1better = False

        p1gene = 0
        p2gene = 0
        while not (p1gene == len(self.genes) and p2gene == len(g.genes)):
            avgene.enable = True

            skip = False

            if p1gene == len(self.genes):
                chosengene = g.genes[p2gene]
                p2gene += 1

                if p1better:
                    skip = True
            elif p2gene == len(g.genes):
                chosengene = self.genes[p1gene]
                p1gene += 1

                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1gene].innovation_num
                p2innov = g.genes[p2gene].innovation_num

                if p1innov == p2innov:
                    av = avgene.lnk
                    p1 = self.genes[p1gene].lnk
                    p2 = self.genes[p2gene].lnk
                    av.link_trait = select_random(p1, p2).link_trait

                    av.weight = p1.weight + p2.weight / 2.0

                    av.in_node = select_random(p1, p2).in_node
                    av.out_node = select_random(p1, p2).out_node
                    av.is_recurrent = select_random(p1, p2).is_recurrent

                    avgene.innovation_num = self.genes[p1gene].innovation_num
                    avgene.mutation_num = (
                        self.genes[p1gene].mutation_num + g.genes[p2gene].mutation_num
                    ) / 2.0

                    if not (self.genes[p1gene].enable and g.genes[p2gene].enable):
                        if random() < 0.75:
                            avgene.enable = False

                    chosengene = avgene
                    p1gene += 1
                    p2gene += 1
                elif p1innov < p2innov:
                    chosengene = self.genes[p1gene]
                    p1gene += 1

                    if not p1better:
                        skip = True
                elif p2innov < p1innov:
                    chosengene = g.genes[p2gene]
                    p2gene += 1

                    if p1better:
                        skip = True

            curgene2 = 0
            cg = chosengene.lnk
            while curgene2 != len(newgenes):
                cg2 = newgenes[curgene2].lnk
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
                curgene2 += 1

            if not skip:
                if cg.link_trait is None:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = cg.link_trait.trait_id - self.traits[0].trait_id

                inode = cg.in_node
                onode = cg.out_node

                if inode.node_id < onode.node_id:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1

                    if curnode == len(newnodes):
                        if not inode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                inode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not onode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                onode.node_trait.trait_id - self.traits[0].trait_id
                            )
                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]
                else:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not onode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                onode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]

                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not inode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = (
                                inode.node_trait.trait_id - self.traits[0].trait_id
                            )

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )

                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                newgene = Gene.create_from_gene(
                    chosengene, newtraits[traitnum], new_inode, new_onode
                )

                newgenes.append(newgene)

        del avgene

        return Genome.create_full_genome_specs(genomeid, newtraits, newnodes, newgenes)

    def mate_singlepoint(self, g, genomeid: int):
        assert isinstance(g, Genome)
        newtraits: list[Trait] = []
        newnodes: list[NNode] = []
        newgenes: list[Gene] = []

        newtrait: Trait

        p1innov: float  # Innovation numbers for genes inside parents' Genomes
        p2innov: float
        chosengene: Gene  # Gene chosen for baby to inherit
        traitnum: int  # Number of trait new gene points to
        inode: NNode  # NNodes connected to the chosen Gene
        onode: NNode
        new_inode: NNode
        new_onode: NNode
        nodetraitnum: int  # Trait number for a NNode

        avgene: Gene

        crosspoint: int  # The point in the Genome to cross at
        genecounter: int  # Counts up to the crosspoint
        skip: bool  # Used for skipping unwanted genes

        p2trait = 0
        for p1trait in self.traits:
            newtrait = Trait.create_from_two(
                p1trait, g.traits[p2trait]
            )  # Construct by averaging
            newtraits.append(newtrait)
            p2trait += 1

        avgene = Gene.create_a_trait(None, 0, 0, 0, 0, 0, 0)

        if len(self.genes) < len(g.genes):
            s = self.genes
            o = g.genes
            crosspoint = randint(0, len(self.genes) - 1)
            p1gene = 0
            p2gene = 0
            stopper = len(g.genes)
            p1stop = len(self.genes)
            p2stop = len(g.genes)
        else:
            s = g.genes
            o = self.genes
            crosspoint = randint(0, len(g.genes) - 1)
            p2gene = 0
            p1gene = 0
            stopper = len(self.genes)
            p1stop = len(g.genes)
            p2stop = len(self.genes)

        genecounter = 0  # Ready to count to crosspoint

        skip = False  # Default to not skip a Gene

        while p2gene != stopper:
            avgene.enable = True  # Default to True

            if p1gene == p1stop:
                chosengene = o[p2gene]
                p2gene += 1
            elif p2gene == p2stop:
                chosengene = s[p1gene]
                p1gene += 1
            else:
                p1innov = s[p1gene].innovation_num
                p2innov = o[p2gene].innovation_num

                if p1innov == p2innov:
                    if genecounter < crosspoint:
                        chosengene = s[p1gene]
                    elif genecounter > crosspoint:
                        chosengene = o[p2gene]
                    else:
                        avgene.lnk.link_trait = select_random(
                            s[p1gene], o[p2gene]
                        ).lnk.link_trait

                        avgene.lnk.weight = (
                            s[p1gene].lnk.weight + o[p2gene].lnk.weight
                        ) / 2.0

                        avgene.lnk.in_node = select_random(
                            s[p1gene], o[p2gene]
                        ).lnk.in_node
                        avgene.lnk.out_node = select_random(
                            s[p1gene], o[p2gene]
                        ).lnk.out_node
                        avgene.lnk.is_recurrent = select_random(
                            s[p1gene], o[p2gene]
                        ).lnk.is_recurrent

                        avgene.innovation_num = s[p1gene].innovation_num
                        avgene.mutation_num = (
                            s[p1gene].mutation_num + o[p2gene].mutation_num
                        ) / 2.0

                        if not (s[p1gene].enable and o[p2gene].enable):
                            avgene.enable = False

                        chosengene = avgene

                    p1gene += 1
                    p2gene += 1
                    genecounter += 1
                elif p1innov < p2innov:
                    if genecounter < crosspoint:
                        chosengene = s[p1gene]
                        p1gene += 1
                        genecounter += 1
                    else:
                        chosengene = o[p2gene]
                        p2gene += 1
                elif p2innov < p1innov:
                    p2gene += 1
                    skip = True  # Special case: we need to skip to the next iteration

            curgene2 = 0

            ng2 = newgenes[curgene2].lnk
            cg = chosengene.lnk
            while curgene2 != len(newgenes) and not (
                (
                    ng2.in_node.node_id == cg.in_node.node_id
                    and ng2.out_node.node_id == cg.out_node.node_id
                    and ng2.is_recurrent == cg.is_recurrent
                )
                or (
                    ng2.in_node.node_id == cg.out_node.node_id
                    and ng2.out_node.node_id == cg.in_node.node_id
                    and not (ng2.is_recurrent or cg.is_recurrent)
                )
            ):
                curgene2 += 1

            if curgene2 != len(newgenes):
                skip = True  # Link is a duplicate

            if not skip:
                if cg.link_trait is None:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = (
                        cg.link_trait.trait_id - self.traits[0].trait_id
                    )  # The subtracted number normalizes depending on whether traits start counting at 1 or 0

                inode = cg.in_node
                onode = cg.out_node

                if inode.node_id < onode.node_id:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1

                    if curnode == len(newnodes):
                        if not inode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = ((inode.node_trait).trait_id) - (
                                (self.traits[0]).trait_id
                            )

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                    curnode = 0
                    while curnode != len(newnodes) and (
                        newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not (onode.node_trait):
                            nodetraitnum = 0
                        else:
                            nodetraitnum = ((onode.node_trait).trait_id) - (
                                self.traits[0]
                            ).trait_id

                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]
                else:
                    curnode = 0
                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != onode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not onode.node_trait:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = ((onode.node_trait).trait_id) - (
                                self.traits[0]
                            ).trait_id

                        new_onode = NNode.create_from_nnode_and_trait(
                            onode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_onode)
                    else:
                        new_onode = newnodes[curnode]

                    curnode = 0

                    while (
                        curnode != len(newnodes)
                        and newnodes[curnode].node_id != inode.node_id
                    ):
                        curnode += 1
                    if curnode == len(newnodes):
                        if not (inode.node_trait):
                            nodetraitnum = 0
                        else:
                            nodetraitnum = ((inode.node_trait).trait_id) - (
                                self.traits[0]
                            ).trait_id

                        new_inode = NNode.create_from_nnode_and_trait(
                            inode, newtraits[nodetraitnum]
                        )
                        self.node_insert(newnodes, new_inode)
                    else:
                        new_inode = newnodes[curnode]

                new_gene = Gene.create_from_gene(
                    chosengene, newtraits[traitnum], new_inode, new_onode
                )
                newgenes.append(new_gene)

            skip = False

        del avgene  # Clean up used object

        return Genome.create_full_genome_specs(genomeid, newtraits, newnodes, newgenes)

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
            disjoint_coeff * (num_disjoint / 1.0)
            + excess_coeff * (num_excess / 1.0)
            + mutdiff_coeff * (mut_diff_total / num_matching)
        )

    def trait_compare(self, t1: Trait, t2: Trait) -> float:
        id1 = t1.trait_id
        id2 = t2.trait_id
        params_diff = 0.0

        if id1 == 1 and id2 >= 2 or id2 == 1 and id1 >= 2:
            return 0.5
        if id1 < 2:
            return 0.0

        for count in range(3):
            params_diff += abs(t1.params[count] - t2.params[count])
        return params_diff / 4.0

    def extrons(self) -> int:
        return len([curgene for curgene in self.genes if curgene.enable])

    def randomize_traits(self):
        numtraits = len(self.traits)
        traitnum: int

        for curnode in self.nodes:
            traitnum = randint(1, numtraits)
            curnode.trait_id = traitnum

            curtrait = 0
            while (self.traits[curtrait].trait_id) != traitnum:
                curtrait += 1
            curnode.node_trait = self.traits[curtrait]

        for curgene in self.genes:
            traitnum = randint(1, numtraits)
            curgene.lnk.trait_id = traitnum

            curtrait = 0
            while self.traits[curtrait].trait_id != traitnum:
                curtrait += 1
            curgene.lnk.link_trait = self.traits[curtrait]

    def node_insert(self, nlist: list[NNode], n: NNode):
        id = n.node_id

        curnode = 0
        while nlist[curnode] != nlist[-1] and (nlist[curnode].node_id < id):
            curnode += 1

        nlist.insert(curnode, n)

    def add_gene(self, glist: list[Gene], g: Gene):
        inum = g.innovation_num

        curgene = 0
        while glist[curgene] != glist[-1] and (glist[curgene].innovation_num < inum):
            curgene += 1

        glist.insert(curgene, g)
