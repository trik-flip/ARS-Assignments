from link import Link
from nnode import NNode
from trait import Trait


class Gene:
    lnk: Link
    innovation_num: float
    mutation_num: float
    enable: bool
    frozen: bool

    @staticmethod
    def create_no_trait(
        w: float, inode: NNode, onode: NNode, recur: bool, innov: float, mnum: float
    ):
        g = Gene()
        g.lnk = Link.create_no_trait(w, inode, onode, recur)
        g.innovation_num = innov
        g.mutation_num = mnum
        g.enable = True
        g.frozen = False
        return g

    @staticmethod
    def create_a_trait(
        tp: Trait | None,
        w: float,
        inode: NNode,
        onode: NNode,
        recur: bool,
        innov: float,
        mnum: float,
    ):
        g = Gene()
        g.lnk = Link.create_from_trait(tp, w, inode, onode, recur)
        g.innovation_num = innov
        g.mutation_num = mnum

        g.enable = True

        g.frozen = False
        return g

    @staticmethod
    def create_from_gene(o, tp: Trait | None, inode: NNode, onode: NNode):
        assert isinstance(o, Gene)

        g = Gene()
        g.lnk = Link.create_from_trait(
            tp, o.lnk.weight, inode, onode, o.lnk.is_recurrent
        )
        g.innovation_num = o.innovation_num
        g.mutation_num = o.mutation_num
        g.enable = o.enable
        g.frozen = o.frozen
        return g
