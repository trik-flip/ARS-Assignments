from random import random

from neat import rand_pos_neg


class Trait:
    trait_id: int
    params: list[float]

    def __init__(self) -> None:
        self.params = [0 for _ in range(8)]

    @staticmethod
    def create_from_manual(id: int, *p: float):
        assert len(p) == 8
        t = Trait()
        t.params = [*p]
        t.trait_id = id
        return t

    @staticmethod
    def create_from_one(t1):
        assert isinstance(t1, Trait)
        t = Trait()
        for i, p in enumerate(t.params):
            t.params[i] = t1.params[i]
        t.trait_id = t1.trait_id
        return t

    @staticmethod
    def create_from_two(t1, t2):
        assert isinstance(t1, Trait)
        assert isinstance(t2, Trait)
        t = Trait()
        for i, p in enumerate(t.params):
            t.params[i] = (t1.params[i] + t2.params[i]) / 2
        t.trait_id = t1.trait_id
        return t

    def mutate(self):
        for i, p in enumerate(self.params):
            if random() > 0.5:
                self.params[i] += rand_pos_neg() * random() * 4
                if self.params[i] < 0:
                    self.params[i] = 0
                if self.params[i] > 1:
                    self.params[i] = 1
