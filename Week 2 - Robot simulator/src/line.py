from position import Position
from math import atan, cos
from functools import cache


class Line:
    start: Position
    end: Position

    def len(self):
        return (
            (self.start.x - self.end.x) ** 2 + (self.start.y - self.end.y) ** 2
        ) ** (1 / 2)

    def distance_to(self, point: Position):
        if abs(self.gradient()) > 1e15:
            min_y = min(self.start.y, self.end.y)
            max_y = max(self.start.y, self.end.y)
            if min_y <= point.y <= max_y:
                return abs(self.start.x - point.x)
            else:
                return self._point_distance_to(point)

        if abs(self.gradient()) < 1e-2:
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

        max_x = max(self.start.x, self.end.x, point.x)
        max_y = self.perpendicular_gradient() * max_x
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
        y = point.y_axis_intersect(self.perpendicular_gradient())

        y1 = self.start.y_axis_intersect(self.perpendicular_gradient())
        y2 = self.end.y_axis_intersect(self.perpendicular_gradient())
        min_y = min(y1, y2)
        max_y = max(y1, y2)

        return min_y <= y and y <= max_y

    def __init__(self, x1, y1, x2, y2) -> None:
        self.start = Position(x1, y1)
        self.end = Position(x2, y2)

    @cache
    def to_tuple(self):
        return self.start.to_tuple(), self.end.to_tuple()

    @cache
    def radians(self):
        return atan(self.gradient())

    @cache
    def gradient(self):
        if self.start.x == self.end.x:
            return float("inf")
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    @cache
    def perpendicular_gradient(self):
        return -1 / self.gradient()

    @cache
    def y_axis_intersect(self, gr: float | None = None):
        if gr is None:
            gr = self.gradient()
        return self.start.y - gr * self.start.x

    def strict_intersect_point(self, line):
        p = self.intersect_point(line)
        if p is None:
            raise Exception("p can't be None")
        return p

    def intersect_point(self, line):
        assert isinstance(line, Line)

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

    def intersect_point_with_radius(self, line, r: float):
        assert isinstance(line, Line)

        new_l = line.copy()

        if abs(line.gradient()) < 1e-2:
            # If I'm above the line, I should stay above the line
            if self.start.y > line.start.y:
                new_l.start.y += r
                new_l.end.y += r
            else:
                new_l.start.y -= r
                new_l.end.y -= r
            return self.strict_intersect_point(new_l)
        if abs(line.gradient()) > 1e15:
            if self.start.x > line.start.x:
                new_l.start.x += r
                new_l.end.x += r
            else:
                new_l.start.x -= r
                new_l.end.x -= r
            return self.strict_intersect_point(new_l)

        # get gradient of line
        delta = r / cos(line.radians())

        # TODO(step 2): move line in the perpendicular direction with r

        if line < self:
            new_l.start.y += delta
            new_l.end.y += delta
        # else if above the line
        else:
            new_l.start.y -= delta
            new_l.end.y -= delta

        # TODO(step 3): calc new intersection_point
        p = self.strict_intersect_point(new_l)
        return p

    def __lt__(self, o):
        if isinstance(o, Line):
            return self.y_axis_intersect() < o.y_axis_intersect(self.gradient())
        if isinstance(o, Position):
            return self.y_axis_intersect() < o.y - self.gradient() * o.x

        return NotImplemented

    @cache
    def __repr__(self) -> str:
        return f"({self.start}), ({self.end})"

    def copy(self):
        return Line(self.start.x, self.start.y, self.end.x, self.end.y)

    def does_intersect(self, line):
        assert isinstance(line, Line)

        p = self.intersect_point(line)

        if p is None:
            return False

        return self.point_in_range_of_line(p) and line.point_in_range_of_line(p)

    def point_in_range_of_line(self, p):
        max_x = max(self.end.x, self.start.x)
        min_x = min(self.start.x, self.end.x)

        max_y = max(self.end.y, self.start.y)
        min_y = min(self.start.y, self.end.y)

        return (min_x <= p.x and p.x <= max_x) and (min_y <= p.y and p.y <= max_y)
