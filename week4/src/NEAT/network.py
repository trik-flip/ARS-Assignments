from nnode import NNode, NodeType, FuncType
from genome import Genome
from neat import fsigmoid, hebbian


class Network:
    numnodes: int
    numlinks: int
    all_nodes: list[NNode]
    input_iter: int
    genotype: Genome
    name: str | None
    inputs: list[NNode]
    outputs: list[NNode]
    net_id: int
    max_weight: float
    adaptable: bool

    def __init__(self) -> None:
        self.numnodes = -1
        self.numlinks = -1
        self.name = None

    @staticmethod
    def create_with_lists(
        inn: list[NNode],
        out: list[NNode],
        all: list[NNode],
        netid: int,
        adaptval=False,
    ):
        n = Network()
        n.inputs = inn
        n.outputs = out
        n.all_nodes = all
        n.net_id = netid
        n.adaptable = adaptval
        return n

    @staticmethod
    def create_from_netid(net_id: int, adapt_val=False):
        n = Network()
        n.net_id = net_id
        n.adaptable = adapt_val
        return n

    def flush(self):
        for n in self.outputs:
            n.flushback()

    def flush_check(self):
        seen_list = []
        for n in self.outputs:
            location = seen_list.index(n)
            if location == len(seen_list) - 1:
                seen_list.append(n)
                n.flushback_check(seen_list)

    def outputs_off(self):
        for n in self.outputs:
            if (n.activation_count) == 0:
                return True

        return False

    def activate(self):
        add_amount: float
        onetime: bool
        abort_count = 0

        onetime = False

        while self.outputs_off() or not onetime:
            abort_count += 1

            if abort_count == 20:
                return False
            for n in self.all_nodes:
                if n.type != NodeType.SENSOR:
                    n.active_sum = 0
                    n.active_flag = False

                    for l in n.incoming:
                        assert l.in_node is not None
                        add_amount = l.weight
                        if not l.time_delay:
                            add_amount *= l.in_node.get_active_out()
                            if (
                                l.in_node.active_flag
                                or l.in_node.type == NodeType.SENSOR
                            ):
                                n.active_flag = True
                            n.active_sum += add_amount
                        else:
                            add_amount *= l.in_node.get_active_out_td()
                            n.active_sum += add_amount

            for n in self.all_nodes:
                if n.type != NodeType.SENSOR and n.active_flag:
                    n.last_activation2 = n.last_activation
                    n.last_activation = n.activation

                    if n.override:
                        n.activate_override()
                    else:
                        if n.ftype == FuncType.SIGMOID:
                            n.activation = fsigmoid(n.active_sum, 4.924273, 2.4621365)
                    n.activation_count += 1

            onetime = True

        if self.adaptable:
            for n in self.all_nodes:
                if n.type != NodeType.SENSOR:
                    for l in n.incoming:
                        if l.trait_id in {2, 3, 4}:
                            assert l.in_node is not None
                            assert l.out_node is not None
                            if l.is_recurrent:
                                l.weight = hebbian(
                                    l.weight,
                                    self.max_weight,
                                    l.in_node.last_activation,
                                    l.out_node.get_active_out(),
                                    l.params[0],
                                    l.params[1],
                                    l.params[2],
                                )
                            else:
                                l.weight = hebbian(
                                    l.weight,
                                    self.max_weight,
                                    l.in_node.get_active_out(),
                                    l.out_node.get_active_out(),
                                    l.params[0],
                                    l.params[1],
                                    l.params[2],
                                )
        return True

    def show_activation(self):
        count = len(self.outputs)
        print(count)

    def show_input(self):
        count = len(self.inputs)
        print(count)

    def add_input(self, in_node: NNode):
        self.inputs.append(in_node)

    def add_output(self, out_node: NNode):
        self.outputs.append(out_node)

    def load_sensors(self, sens_vals: list[float]):
        for sp, vp in zip(self.inputs, sens_vals):
            if sp.type == NodeType.SENSOR:
                sp.sensor_load(vp)

    def override_outputs(self, out_vals: float):
        for o in self.outputs:
            o.override_output(out_vals)
            out_vals += 1

    def give_name(self, newname: str):
        self.name = newname

    def node_count(self):
        counter = 0
        seen_list: list[NNode] = []
        for n in self.outputs:
            location = seen_list.index(n)
            if location == len(seen_list) - 1:
                counter += 1
                seen_list.append(n)
                self.node_count_helper((n), counter, seen_list)

        self.numnodes = counter

        return counter

    def node_count_helper(self, node: NNode, counter: int, seenlist: list[NNode]):
        in_nodes = node.incoming
        if node.type != NodeType.SENSOR:
            for l in in_nodes:
                assert l.in_node is not None
                location = seenlist.index(l.in_node)
                if location == len(seenlist) - 1:
                    counter += 1
                    seenlist.append(l.in_node)
                    self.node_count_helper(l.in_node, counter, seenlist)

    def linkcount(self):
        counter = 0
        seenlist = []

        for n in self.outputs:
            self.link_count_helper(n, counter, seenlist)

        self.numlinks = counter

        return counter

    def link_count_helper(self, node: NNode, counter: int, seenlist: list[NNode]):
        in_links = node.incoming

        location = seenlist.index(node)
        if node.type == NodeType.SENSOR and location == len(seenlist) - 1:
            seenlist.append(node)

            for l in in_links:
                counter += 1
                assert l.in_node is not None
                self.link_count_helper(l.in_node, counter, seenlist)

    def destroy_helper(self, curnode: NNode, seenlist: list[NNode]):
        in_nodes = curnode.incoming

        if curnode.type != NodeType.SENSOR:
            for l in in_nodes:
                assert l is not None
                location = seenlist.index(l)
                if location == len(seenlist) - 1:
                    assert l.in_node is not None
                    seenlist.append(l.in_node)
                    self.destroy_helper(l.in_node, seenlist)

    def is_recur(
        self, pot_in_node: NNode, pot_out_node: NNode, count: int, thresh: int
    ):
        count += 1

        if count > thresh:
            return False

        if pot_in_node == pot_out_node:
            return True

        for l in pot_in_node.incoming:
            assert l.in_node is not None
            if not (l.is_recurrent) and self.is_recur(
                l.in_node, pot_out_node, count, thresh
            ):
                return True
        return False

    def input_start(self):
        self.input_iter = 0
        return 1

    def load_in(self, d: float):
        self.inputs[self.input_iter].sensor_load(d)
        self.input_iter += 1
        if self.input_iter == len(self.inputs) - 1:
            return 0
        return 1

    def max_depth(self):
        return max([out.depth(0, self) for out in self.outputs])
