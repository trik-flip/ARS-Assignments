from position import Position
from math import atan


class Line:
    start: Position
    end: Position

    def distance_to(self, point: Position):
        if self.gradient() > 1e15:
            min_y = min(self.start.y, self.end.y)
            max_y = max(self.start.y, self.end.y)
            if min_y <= point.y <= max_y:
                return abs(self.start.x - point.x)
            else:
                return self._point_distance_to(point)

        if self.gradient() < 1e-2:
            min_x = min(self.start.x, self.end.x)
            max_x = max(self.start.x, self.end.x)
            if min_x <= point.x <= max_x:
                return abs(self.start.y - point.y)
            else:
                return self._point_distance_to(point)

        if self._in_perpendicular_range(point):
            return self._perpendicular_distance_to(point)
        else:
            return self._point_distance_to(point)

    def _perpendicular_distance_to(self, point: Position):
        # Determine the shortest line
        gradient = -1 / self.gradient()

        max_x = max(self.start.x, self.end.x, point.x)
        max_y = gradient * max_x
        l = Line(point.x, point.y, max_x, max_y)

        # calculate intersection point
        xp = self.intersect_point(l)

        # return distance to intersection point
        return point.distance_to(xp)

    def _point_distance_to(self, point):
        p1_distance = self.start.distance_to(point)
        p2_distance = self.end.distance_to(point)
        return min(p1_distance, p2_distance)

    def _in_perpendicular_range(self, point: Position):
        sg = self.gradient()
        new_gradient = -1 / sg
        y = point.y_axis_intersect(new_gradient)

        y1 = self.start.y_axis_intersect(new_gradient)
        y2 = self.end.y_axis_intersect(new_gradient)
        min_y = min(y1, y2)
        max_y = max(y1, y2)

        return min_y <= y and y <= max_y

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
            return Position(x, y)
        if sg == float("inf") or abs(sg) > 1e15:
            x = self.start.x
            y = ly + x * lg
            return Position(x, y)
        if lg == sg:
            if ly == sy:
                return self.start
            return None

        x = (ly - sy) / (sg - lg)
        y = x * lg + ly
        return Position(x, y)

    def __repr__(self) -> str:
        return f"({self.start}), ({self.end})"
