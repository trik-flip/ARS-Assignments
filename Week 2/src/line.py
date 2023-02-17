from position import Position
from math import atan


class Line:
    start: Position
    end: Position

    def __init__(self, x1, y1, x2, y2) -> None:
        self.start = Position(x1, y1)
        self.end = Position(x2, y2)

    def to_tuple(self):
        return self.start.to_tuple(), self.end.to_tuple()

    def radians(self):
        return atan(self.gradient())

    def gradient(self):
        if self.start.x == self.end.x:
            return float("inf")
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def y_axis_intersect(self):
        return self.start.y - self.gradient() * self.start.x

    def intersect_point(self, line):
        if not isinstance(line, Line):
            return None

        lg = line.gradient()
        sg = self.gradient()
        ly = line.y_axis_intersect()
        sy = self.y_axis_intersect()

        if lg == float("inf") or abs(lg) > 1e15:
            x = line.start.x
            y = sy + x * sg
            return x, y
        if sg == float("inf") or abs(sg) > 1e15:
            x = self.start.x
            y = ly + x * lg
            return x, y
        if lg == sg:
            if ly == sy:
                return self.to_tuple()
            return None

        x = (ly - sy) / (sg - lg)
        y = x * lg + ly
        return x, y
