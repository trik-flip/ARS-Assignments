from nnode import NNode
from trait import Trait


class Link:
    weight: float
    in_node: NNode | None
    out_node: NNode | None
    is_recurrent: bool
    time_delay: bool

    link_trait: Trait | None
    trait_id: int

    added_weight: float
    params: list[float]

    @staticmethod
    def create_no_trait(
        w: float, inode: NNode | None, onode: NNode | None, recur: bool
    ):
        l = Link()
        l.weight = w
        l.in_node = inode
        l.out_node = onode
        l.is_recurrent = recur
        l.added_weight = 0
        l.link_trait = None
        l.time_delay = False
        l.trait_id = 1
        return l

    @staticmethod
    def create_from_trait(
        lt: Trait | None,
        w: float,
        inode: NNode | None,
        onode: NNode | None,
        recur: bool,
    ):
        l = Link()
        l.weight = w
        l.in_node = inode
        l.out_node = onode
        l.is_recurrent = recur
        l.added_weight = 0
        l.link_trait = lt
        l.time_delay = False
        if lt is not None:
            l.trait_id = lt.trait_id
        else:
            l.trait_id = 1
        return l

    @staticmethod
    def create_unknown(w: float):
        l = Link()
        l.weight = w
        l.in_node = None
        l.out_node = None
        l.is_recurrent = False
        l.link_trait = None
        l.time_delay = False
        l.trait_id = 1
        return l

    def derive_trait(self, trait: Trait | None):
        if trait is not None:
            for i in range(8):
                self.params[i] = trait.params[i]
            self.trait_id = trait.trait_id
        else:
            for i in range(8):
                self.params[i] = 0
            self.trait_id = 1
