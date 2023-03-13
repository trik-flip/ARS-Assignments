from enum import Enum
from typing import Self

from link import Link
from network import Network
from trait import Trait


class NodeType(Enum):
    NEURON = 0
    SENSOR = 1


class NodePlace(Enum):
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2
    BIAS = 3


class FuncType(Enum):
    SIGMOID = 0


class NNode:
    activation_count: int
    last_activation: float
    last_activation2: float

    node_trait: Trait | None

    trait_id: int
    dup: Self

    analogue: Self

    override: bool

    override_value: float

    frozen: bool
    func_type: FuncType
    type: NodeType
    active_sum: float
    activation: float
    active_flag: bool

    output: float
    params: list[float]
    incoming: list[Link]
    outgoing: list[Link]

    row_levels: list[float]
    row: int
    y_pos: int
    x_pos: int

    node_id: int

    gen_node_label: NodePlace

    def __init__(self) -> None:
        self.active_flag = False
        self.active_sum = 0
        self.activation = 0
        self.output = 0

        self.last_activation = 0
        self.last_activation2 = 0
        self.activation_count = 0
        self.ftype = FuncType.SIGMOID
        self.node_trait = None
        self.dup = 0
        self.analogue = 0
        self.frozen = False
        self.trait_id = 1
        self.override = False

    def override_output(self, new_output):
        self.override_value = new_output
        self.override = True

    @staticmethod
    def create_from_nodetype(
        node_type: NodeType, node_id: int, placement=NodePlace.HIDDEN
    ):
        nn = NNode()
        nn.type = node_type
        nn.node_id = node_id
        nn.gen_node_label = placement
        return nn

    @staticmethod
    def create_from_nnode_and_trait(n, t: Trait | None):
        assert isinstance(n, NNode)
        nn = NNode()
        nn.type = n.type
        nn.node_id = n.node_id
        nn.gen_node_label = n.gen_node_label
        nn.node_trait = t
        if t is not None:  # is not None (?)
            nn.trait_id = t.trait_id
        else:
            nn.trait_id = 1
        return nn

    def sensor_load(self, val: float):
        if self.type == NodeType.SENSOR:
            self.last_activation2 = self.last_activation
            self.last_activation = self.activation
            self.activation_count += 1
            self.activation = val
            return True
        return False

    def add_incoming_with_recur(self, feed_node, weight: float, recur: bool):
        assert isinstance(feed_node, NNode)
        new_link = Link.create_no_trait(weight, feed_node, self, recur)
        self.incoming.append(new_link)
        feed_node.outgoing.append(new_link)

    def add_incoming(self, feed_node, weight: float):
        assert isinstance(feed_node, NNode)
        new_link = Link.create_no_trait(weight, feed_node, self, False)
        self.incoming.append(new_link)
        feed_node.outgoing.append(new_link)

    def get_active_out(self):
        if self.activation_count > 0:
            return self.activation
        return 0.0

    def get_active_out_td(self):
        if self.activation_count > 1:
            return self.last_activation
        return 0.0

    def flushback(self):
        if self.type == NodeType.SENSOR or self.activation_count > 0:
            self.activation_count = 0
            self.activation = 0
            self.last_activation = 0
            self.last_activation2 = 0
        if self.type == NodeType.SENSOR:
            return

        for l in self.incoming:
            l.added_weight = 0
            assert l.in_node is not None
            if l.in_node.activation_count > 0:
                l.in_node.flushback()

    def flushback_check(self, seen_list: list):
        location: int

        if self.activation_count > 0:
            print("ALERT: ", self, " has activation count ", self.activation_count)

        if self.activation > 0:
            print("ALERT: ", self, "has activation", self.activation)

        if self.last_activation > 0:
            print("ALERT: ", self, "has last activation", self.last_activation)

        if self.last_activation2 > 0:
            print("ALERT: ", self, "has last activation2", self.last_activation2)
        if self.type != NodeType.SENSOR:
            for l in self.incoming:
                location = seen_list.index(l.in_node)
                if location == len(seen_list) - 1:
                    seen_list.append(l.in_node)
                    assert l.in_node is not None
                    l.in_node.flushback_check(seen_list)

    def derive_trait(self, current_trait: Trait | None):
        if current_trait is not None:
            for i in range(8):
                self.params[i] = (current_trait.params)[i]
        else:
            for i in range(8):
                self.params[i] = 0

        if current_trait is not None:
            self.trait_id = current_trait.trait_id
        else:
            self.trait_id = 1

    def activate_override(self):
        self.activation = self.override_value
        self.override = False

    def depth(self, d: int, my_net: Network):
        if d > 100:
            return 10

        max_d = d

        if (self.type) == NodeType.SENSOR:
            return d

        for l in self.incoming:
            assert l.in_node is not None
            cur_depth = l.in_node.depth(d + 1, my_net)
            if cur_depth > max_d:
                max_d = cur_depth

        return max_d
