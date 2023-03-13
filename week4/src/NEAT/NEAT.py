from random import random, randint
from math import exp


def rand_pos_neg():
    if randint(1, 10) % 2:
        return 1
    return -1


def fsigmoid(activesum: float, slope: float, constant: float = 0):
    return 1 / (1 + (exp(-(slope * activesum))))


def hebbian(
    weight: float,
    max_weight: float,
    active_in: float,
    active_out: float,
    hebb_rate: float,
    pre_rate: float,
    post_rate: float,
):
    neg = False
    delta: float

    if max_weight < 5.0:
        max_weight = 5.0

    if weight > max_weight:
        weight = max_weight

    if weight < -max_weight:
        weight = -max_weight

    if weight < 0:
        neg = True
        weight = -weight

    top_weight = weight + 2.0
    if top_weight > max_weight:
        top_weight = max_weight

    if not (neg):
        delta = hebb_rate * (
            max_weight - weight
        ) * active_in * active_out + pre_rate * top_weight * active_in * (
            active_out - 1.0
        )
        return weight + delta

    delta = (
        pre_rate * (max_weight - weight) * active_in * (1.0 - active_out)
        + -hebb_rate * (top_weight + 2.0) * active_in * active_out
        + 0
    )

    return -(weight + delta)
