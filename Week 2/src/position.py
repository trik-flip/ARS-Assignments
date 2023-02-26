from math import sqrt


class Position:
    x: float
    y: float

    def distance_to(self, other: object):
        assert isinstance(other, Position)
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x, self.y

    def to_tuple_with_movement(self, x, y):
        return self.x + x, self.y + y

    def __repr__(self) -> str:
        return f"{self.x}, {self.y}"

    def y_axis_intersect(self, gradient):
        return self.y - self.x * gradient
