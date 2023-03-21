from typing import Any
from numpy import array
from .position import Position


class Pose:
    _position: Position
    _direction: float

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
