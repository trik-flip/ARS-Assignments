from math import atan, cos, atan2

from .position import Position


class Line:
    start: Position
    end: Position

    def __init__(self, p1: tuple[float, float], p2: tuple[float, float]) -> None:
        self.start = Position(*p1)
        self.end = Position(*p2)

    def len(self):
        return self.start.d(self.end)

    @property
    def radians(self):
        return atan2(self.dy, self.dx)

    @property
    def dy(self):
        return self.end.dy(self.start)

    @property
    def dx(self):
        return self.end.dx(self.start)

    @property
    def gradient(self):
        if self.dx == 0:
            return float("inf")
        return self.dy / self.dx
