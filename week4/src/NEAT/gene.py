from link import Link
from nnode import NNode
from trait import Trait


class Gene:
    link: Link
    innovation_num: float
    mutation_num: float
    enable: bool
    frozen: bool

    @staticmethod
    def create_no_trait(
        w: float,
        inode: NNode,
        out_node: NNode,
        recur: bool,
        innov: float,
        mutation_num: float,
    ):
        g = Gene()
        g.link = Link.create_no_trait(w, inode, out_node, recur)
        g.innovation_num = innov
        g.mutation_num = mutation_num
        g.enable = True
        g.frozen = False
        return g

    @staticmethod
    def create_a_trait(
        tp: Trait | None,
        w: float,
        in_node: NNode | None,
        out_node: NNode | None,
        recur: bool,
        innovation_num: float,
        mutation_num: float,
    ):
        g = Gene()
        g.link = Link.create_from_trait(tp, w, in_node, out_node, recur)
        g.innovation_num = innovation_num
        g.mutation_num = mutation_num
        g.enable = True
        g.frozen = False
        return g

    @staticmethod
    def create_from_gene(o, t: Trait | None, inn: NNode, onn: NNode):
        assert isinstance(o, Gene)

        g = Gene()
        g.link = Link.create_from_trait(t, o.link.weight, inn, onn, o.link.is_recurrent)
        g.innovation_num = o.innovation_num
        g.mutation_num = o.mutation_num
        g.enable = o.enable
        g.frozen = o.frozen
        return g
