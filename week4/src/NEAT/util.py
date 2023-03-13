from random import random


def select_random(a, b):
    if random() > 0.5:
        return a
    return b
