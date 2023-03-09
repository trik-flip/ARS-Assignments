from random import random
import numpy as np


class EvolutionaryAlgorithmOrganism:
    def __init__(
        self, *, input: int, hidden: list[int] = [], output: int, scaler: float = 1.0
    ) -> None:
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
        assert len(input_data) == len(self.input) - 1

        for i, val in enumerate(input_data):
            self.input[i] = val

        for i, _ in enumerate(self.network[:-2]):
            self.network[i + 1] = np.array([*self.network[i].dot(self.weights[i]), 1])
        self.network[-1] = self.network[-2].dot(self.weights[-1])

        self.output = self.network[-1]
        return self.output

    def cross(self, ea2, c1=0.5, c2=0.5):
        assert isinstance(ea2, EvolutionaryAlgorithmOrganism)
        baby = self.off_spring()

        if np.random.random() > c1:
            self.__cross_over_single_weight(ea2, baby, c2)
        else:
            self.__cross_over_whole_weight(ea2, baby, c2)

        return baby

    def __cross_over_single_weight(self, ea2, baby, change: float):
        assert isinstance(ea2, EvolutionaryAlgorithmOrganism)
        assert isinstance(baby, EvolutionaryAlgorithmOrganism)

        for i, w in enumerate(baby.weights):
            for j, _w in enumerate(baby.weights[i]):
                for ij, _ in enumerate(baby.weights[i][j]):
                    if np.random.random() > change:
                        baby.weights[i][j][ij] = np.array(self.weights[i][j][ij])
                    else:
                        baby.weights[i][j][ij] = np.array(ea2.weights[i][j][ij])

    def difference(self, o) -> float:
        assert isinstance(o, EvolutionaryAlgorithmOrganism)
        diff = 0.0
        for i, w in enumerate(o.weights):
            for j, _w in enumerate(o.weights[i]):
                for ij, _ in enumerate(o.weights[i][j]):
                    diff += abs(self.weights[i][j][ij] - o.weights[i][j][ij])

        return diff

    def __cross_over_whole_weight(self, ea2, baby, chance: float):
        assert isinstance(ea2, EvolutionaryAlgorithmOrganism)
        assert isinstance(baby, EvolutionaryAlgorithmOrganism)

        for i, w in enumerate(baby.weights):
            if np.random.random() > chance:
                baby.weights[i] = self.weights[i]
            else:
                baby.weights[i] = ea2.weights[i]

    def off_spring(self):
        return EvolutionaryAlgorithmOrganism(
            input=len(self.input) - 1,
            hidden=[len(w) - 1 for w in self.hidden],
            output=len(self.output),
        )

    def copy(self):
        baby = self.off_spring()
        for i, w in enumerate(baby.weights):
            # for j, _w in enumerate(baby.weights[i]):
            #     baby.weights[i][j] = np.array(self.weights[i][j])
            baby.weights[i] = np.array(self.weights[i])

        return baby

    def mutate(self, mutation_scaler: float, mutation_chance: float):
        for i, w in enumerate(self.weights):
            for j, n in enumerate(w):
                for ij, _ in enumerate(n):
                    if random() < mutation_chance:
                        self.weights[i][j][ij] = (
                            self.weights[i][j][ij] + np.random.random() - 0.5
                        ) * mutation_scaler

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, EvolutionaryAlgorithmOrganism)
        for i, w in enumerate(self.weights):
            for j, _w in enumerate(w):
                if any(self.weights[i][j] != o.weights[i][j]):
                    return False
        return True
