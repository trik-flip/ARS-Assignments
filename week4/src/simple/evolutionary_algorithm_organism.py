from random import random

import numpy as np


class EvolutionaryAlgorithmOrganism:
    def __init__(
        self,
        *,
        input: int,
        hidden: list[int] = [],
        output: int,
        scaler: float = 1.0,
        recur: None | int = None,
    ) -> None:
        self.recur = recur

        if recur is not None:
            match recur:
                case -1:
                    size_of_recur_layer = output
                case x if abs(x) >= len(hidden) + 2:
                    raise Exception(f"{x} is not a valid value")
                case x if x < 0:
                    size_of_recur_layer = hidden[x + 1]
                case x if x > 0:
                    size_of_recur_layer = hidden[x - 1]
                case x:
                    raise Exception(f"{x} is not a valid value")

            self.size_of_recur_layer = size_of_recur_layer
            self.input = np.zeros(input + 1 + size_of_recur_layer)
        else:
            self.input = np.zeros(input + 1)
        self.input[-1] = 1

        self.hidden = [np.zeros(n + 1) for n in hidden]
        for l in self.hidden:
            l[-1] = 1

        self.output = np.zeros(output)

        self.network = [self.input, *self.hidden, self.output]
        self.weights = []

        for i, layer in enumerate(self.network[:-2]):
            self.weights.append(
                (np.random.rand(len(layer), len(self.network[i + 1]) - 1) - 0.5)
                * scaler
            )
        self.weights.append(
            (np.random.rand(len(self.network[-2]), len(self.network[-1])) - 0.5)
            * scaler
        )

    def run(self, *input_data: float):
        if self.recur is not None:
            if self.recur == -1:
                input_data += tuple(self.network[self.recur])
            else:
                input_data += tuple(self.network[self.recur][:-1])

        assert (
            len(input_data) == len(self.input) - 1
        ), "the input-data size should input-layer size"

        for i, val in enumerate(input_data):
            self.input[i] = val

        for i, w in enumerate(self.network[:-2]):
            self.network[i + 1] = np.array([*w.dot(self.weights[i]), 1])
        self.network[-1] = self.network[-2].dot(self.weights[-1])

        self.output = self.network[-1]
        return self.output

    def cross(self, ea, c1=0.5, c2=0.5):
        assert isinstance(
            ea, EvolutionaryAlgorithmOrganism
        ), f"{ea} should be a EvolutionaryAlgorithmOrganism"
        baby = self.off_spring()

        if np.random.random() > c1:
            self.__cross_over_single_weight(ea, baby, c2)
        else:
            self.__cross_over_whole_weight(ea, baby, c2)

        return baby

    def __cross_over_single_weight(self, ea, baby, change: float):
        assert isinstance(
            ea, EvolutionaryAlgorithmOrganism
        ), f"{ea} should be a EvolutionaryAlgorithmOrganism"
        assert isinstance(
            baby, EvolutionaryAlgorithmOrganism
        ), f"{baby} should be a EvolutionaryAlgorithmOrganism"

        for i, w in enumerate(self.weights):
            for j, _w in enumerate(w):
                for ij, __w in enumerate(_w):
                    if np.random.random() > change:
                        baby.weights[i][j][ij] = np.array(__w)
                    else:
                        baby.weights[i][j][ij] = np.array(ea.weights[i][j][ij])

    def difference(self, o) -> float:
        assert isinstance(
            o, EvolutionaryAlgorithmOrganism
        ), f"{o} should be a EvolutionaryAlgorithmOrganism"
        diff = 0.0
        for i, w in enumerate(self.weights):
            for j, _w in enumerate(w):
                for ij, __w in enumerate(_w):
                    diff += abs(__w - o.weights[i][j][ij])

        return diff

    def __cross_over_whole_weight(self, ea, baby, chance: float):
        assert isinstance(
            ea, EvolutionaryAlgorithmOrganism
        ), f"{ea} should be a EvolutionaryAlgorithmOrganism"
        assert isinstance(
            baby, EvolutionaryAlgorithmOrganism
        ), f"{baby} should be a EvolutionaryAlgorithmOrganism"

        for i, w in enumerate(self.weights):
            if np.random.random() > chance:
                baby.weights[i] = w
            else:
                baby.weights[i] = ea.weights[i]

    def off_spring(self):
        input_length = len(self.input)
        if self.recur is not None:
            input_length -= [len(n) for n in self.network][self.recur]
        else:
            input_length -= 1
        return EvolutionaryAlgorithmOrganism(
            input=input_length,
            hidden=[len(w) - 1 for w in self.hidden],
            output=len(self.output),
            recur=self.recur,
        )

    def copy(self):
        baby = self.off_spring()
        for i, w in enumerate(self.weights):
            baby.weights[i] = np.array(w)

        return baby

    def mutate(self, mutation_scaler: float, mutation_chance: float):
        for i, w in enumerate(self.weights):
            for j, _w in enumerate(w):
                for ij, __w in enumerate(_w):
                    if random() < mutation_chance:
                        self.weights[i][j][ij] = (
                            __w + np.random.random() - 0.5
                        ) * mutation_scaler

    def __eq__(self, o: object) -> bool:
        assert isinstance(
            o, EvolutionaryAlgorithmOrganism
        ), f"{o} should be a EvolutionaryAlgorithmOrganism"
        for sw, ow in zip(self.weights, o.weights):
            for _sw, _ow in zip(sw, ow):
                if any(_sw != _ow):
                    return False
        # for i, w in enumerate(self.weights):
        #     for j, _w in enumerate(w):
        #         if any(_w != o.weights[i][j]):
        #             return False
        return True
