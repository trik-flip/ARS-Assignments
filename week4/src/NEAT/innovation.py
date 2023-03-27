from innovation_type import InnovationType


class Innovation:
    innovation_type: InnovationType
    node_in_id: int
    node_out_id: int
    innovation_num1: float
    innovation_num2: float
    new_weight: float
    new_trait_number: int
    new_node_id: int
    old_innovation_num: float
    recur_flag: bool

    @staticmethod
    def create_innovation(
        n_in: int,
        n_out: int,
        num1: float,
        num2: float,
        new_id: int,
        old_innovation: float,
    ):
        inv = Innovation()
        inv.innovation_type = InnovationType.NEW_NODE
        inv.node_in_id = n_in
        inv.node_out_id = n_out
        inv.innovation_num1 = num1
        inv.innovation_num2 = num2
        inv.new_node_id = new_id
        inv.old_innovation_num = old_innovation

        inv.new_weight = 0
        inv.new_trait_number = 0
        inv.recur_flag = False
        return inv

    @staticmethod
    def create_link_innovation(n_in: int, n_out: int, num1: float, w: float, t: int):
        inv = Innovation()
        inv.innovation_type = InnovationType.NEW_LINK
        inv.node_in_id = n_in
        inv.node_out_id = n_out
        inv.innovation_num1 = num1
        inv.new_weight = w
        inv.new_trait_number = t

        inv.innovation_num2 = 0
        inv.new_node_id = 0
        inv.recur_flag = False
        return inv

    @staticmethod
    def create_recur_link_innovation(
        n_in: int, n_out: int, num1: float, w: float, t: int, recur: bool
    ):
        inv = Innovation()
        inv.innovation_type = InnovationType.NEW_LINK
        inv.node_in_id = n_in
        inv.node_out_id = n_out
        inv.innovation_num1 = num1
        inv.new_weight = w
        inv.new_trait_number = t

        inv.innovation_num2 = 0
        inv.new_node_id = 0
        inv.recur_flag = recur
        return inv
