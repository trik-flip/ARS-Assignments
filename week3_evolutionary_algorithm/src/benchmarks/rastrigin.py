import numpy as np


def _rastrigin(x, n, A):
    """Min at x = 0"""
    points = np.linspace(-x, x, n)
    return A * n + sum([y**2 - A * np.cos(2 * np.pi * y) for y in points])


def rastrigin(*x: tuple[float, ...], A=10):
    """Min at (x=0, y=0)"""
    return sum(_rastrigin(i, len(x), A) for i in x)
