from math import atan2
from typing import Any
from numpy import array
from .position import Position


class Pose:
    _position: Position
    _direction: float

    def copy(self):
        p = Pose(self.position.copy(), self._direction)
        return p

    def __eq__(self, o):
        assert isinstance(o, Pose)
        return (
            abs(self._direction - o._direction) < 1e-2 and self.position == o.position
        )

    def __add__(self, value):
        p = self.copy()
        x, y, t = value
        p._position += Position(x, y)
        p._direction += t
        return p

    def __init__(self, init_position, init_direction=0.0) -> None:
        self._position = init_position
        self._direction = init_direction

    @property
    def array(self):
        return array([self._position.x, self._position.y, self._direction])

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        x, y = value
        self._position.x = x
        self._position.y = y

    def calc_position_with_bearing(self, b1, b2):
        assert isinstance(b1, Position)
        assert isinstance(b2, Position)

        x1, y1 = self.position.dxy(b1)
        x2, y2 = self.position.dxy(b2)

        bearing1 = self._direction - atan2(y1, x1)
        bearing2 = self._direction - atan2(y2, x2)

        possible_pos = self.position.intersection_of_beacon(b1, b2)
        if possible_pos is None:
            return None

        p1, p2 = possible_pos
        xp1, yp1 = p1.dxy(b1)
        xp2, yp2 = p2.dxy(b1)

        p1bearing1 = self._direction - atan2(xp1, yp1)
        p2bearing1 = self._direction - atan2(xp2, yp2)

        #TODO: Pose(Position(xp1, yp1),)
