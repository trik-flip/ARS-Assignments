from math import cos, sin
from numpy.random import normal as random


class Position:
    x: float
    y: float

    @staticmethod
    def place_with_noise(x, y, k=1):
        return Position(x + random(scale=k), y + random(scale=k))

    def d(self, other: object):
        assert isinstance(other, Position)
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** (1 / 2)

    def dxy(self, other: object):
        assert isinstance(other, Position)
        return self.dx(other), self.dy(other)

    def dy(self, o):
        assert isinstance(o, Position)
        return self.y - o.y

    def dx(self, o):
        assert isinstance(o, Position)
        return self.x - o.x

    def triangulate_with_beacons(self, b1, b2, b3):
        assert isinstance(b1, Position)
        assert isinstance(b2, Position)
        assert isinstance(b3, Position)

        pc1 = self.intersection_of_beacon(b1, b2)
        pc2 = self.intersection_of_beacon(b1, b3)
        if pc2 is None or pc1 is None:
            return None

        p1, p2 = pc2
        p3, p4 = pc1
        if p1 == p3 or p1 == p4:
            return p1
        return p2

    def intersection_of_beacon(self, b1, b2):
        assert isinstance(b1, Position)
        assert isinstance(b2, Position)
        r1 = self.d(b1)
        r2 = self.d(b2)
        # source: https://www.xarg.org/2016/07/calculate-the-intersection-points-of-two-circles/
        d = b1.d(b2)
        if d <= (r1 + r2) and d >= abs(r2 - r1) and r1 < 200 and r2 < 200:
            ex = b2.dx(b1) / d
            ey = b2.dy(b1) / d

            x = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
            y = sqrt(r1 * r1 - x * x)

            p1 = Position(b1.x + x * ex - y * ey, b1.y + x * ey + y * ex)
            p2 = Position(b1.x + x * ex + y * ey, b1.y + x * ey - y * ex)
            return p1, p2
        return None

    def triangulate(self, r1: float, o2, r2: float, o3, r3: float):
        assert isinstance(o2, Position)
        assert isinstance(o3, Position)

        pc1 = self.intersection_of_circles(r1, o2, r2)
        pc2 = self.intersection_of_circles(r1, o3, r3)
        if pc1 is None or pc2 is None:
            return None

        p1, p2 = pc1
        p3, p4 = pc2
        if p1 == p3 or p1 == p4:
            return p1
        return p2

    def intersection_of_circles(self, r1: float, o2, r2: float):
        assert isinstance(o2, Position)
        # source: https://www.xarg.org/2016/07/calculate-the-intersection-points-of-two-circles/
        d = self.d(o2)
        if d <= (r1 + r2) and d >= abs(r2 - r1) and r1 < 200 and r2 < 200:
            ex = o2.dx(self) / d
            ey = o2.dy(self) / d

            x = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
            y = sqrt(r1 * r1 - x * x)

            p1 = Position(self.x + x * ex - y * ey, self.y + x * ey + y * ex)
            p2 = Position(self.x + x * ex + y * ey, self.y + x * ey - y * ex)
            return p1, p2
        return None

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, o):
        assert isinstance(o, Position)
        p = self.copy()
        p.x += o.x
        p.y += o.y
        return p

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, Position)
        return self.d(o) < 1e-2

    def add_polar(self, length: float, direction: float):
        return self + Position.create_polar(length, direction)

    @staticmethod
    def create_polar(length: float, direction: float):
        return Position(length * cos(direction), length * sin(direction))

    @property
    def xy(self):
        return self.x, self.y

    def copy(self):
        return Position(*self.xy)


def sqrt(x: int | float) -> float:
    return x ** (1 / 2)
