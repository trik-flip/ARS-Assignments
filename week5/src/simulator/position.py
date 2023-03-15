from math import cos, sin


class Position:
    x: float
    y: float

    def d(self, other: object):
        assert isinstance(other, Position)
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** (1 / 2)

    def dy(self, o):
        assert isinstance(o, Position)
        return self.y - o.y

    def dx(self, o):
        assert isinstance(o, Position)
        return self.x - o.x

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
        else:
            return p2

    def intersection_of_circles(self, r1: float, o2, r2: float):
        assert isinstance(o2, Position)
        # source: https://www.xarg.org/2016/07/calculate-the-intersection-points-of-two-circles/
        d = self.d(o2)
        if d <= (r1 + r2) and d >= abs(r2 - r1) and r1 < 200 and r2 < 200:
            ex = o2.dx(self) / d
            ey = o2.dy(self) / d

            x = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
            y = (r1 * r1 - x * x) ** (1 / 2)

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
        return abs(self.dx(o)) < 1e-2 and abs(self.dy(o)) < 1e-2

    @staticmethod
    def create_polar(length, direction):
        return Position(length * cos(direction), length * sin(direction))

    @property
    def xy(self):
        return self.x, self.y

    def copy(self):
        return Position(*self.xy)
