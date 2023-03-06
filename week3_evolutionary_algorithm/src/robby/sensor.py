from math import cos, sin, tan

from .line import Line
from .position import Position


class Sensor:
    position: Position
    offset: float
    direction: float
    value: float

    def __init__(self, x, y, direction) -> None:
        self.position = Position(x, y)
        self.offset = direction
        self.direction = direction

    def does_intersect(self, line: Line):
        if line.gradient() == self.gradient():
            return False

        point = self.intersect_point(line)
        if point is None:
            return False

        going_right = 0 < cos(self.direction)
        going_up = 0 < sin(self.direction)

        if self.position.x > point.x and going_right:
            return False
        if self.position.x < point.x and not going_right:
            return False

        if self.position.y > point.y and going_up:
            return False
        if self.position.y < point.y and not going_up:
            return False

        small_x = min(line.start.x, line.end.x)
        big_x = max(line.start.x, line.end.x)
        if point.x < small_x - 0.1 or point.x > big_x + 0.1:
            return False

        small_y = min(line.start.y, line.end.y)
        big_y = max(line.start.y, line.end.y)
        if point.y < small_y - 0.1 or point.y > big_y + 0.1:
            return False

        return True

    def intersect_point(self, line: Line):
        l_g = line.gradient()
        s_g = self.gradient()

        if l_g == float("inf") or abs(l_g) > 1e15:
            x = line.start.x
            y = self.__y_axis_intersect() + x * s_g
            return Position(x, y)

        if s_g == float("inf") or abs(s_g) > 1e15:
            x = self.position.x
            y = line.y_axis_intersect() + x * l_g
            return Position(x, y)

        if l_g == s_g:
            if line.y_axis_intersect() == self.__y_axis_intersect():
                return self.position
            return None

        y1 = self.__y_axis_intersect()
        x = (line.y_axis_intersect() - y1) / (s_g - l_g)
        y = self.gradient() * x + y1
        return Position(x, y)

    def gradient(self):
        return tan(self.direction)

    def __y_axis_intersect(self):
        return self.position.y - self.position.x * self.gradient()
