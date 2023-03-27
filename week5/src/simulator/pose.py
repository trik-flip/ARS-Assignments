from math import atan2

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

    def _bearing(self, b: Position, angle=None):
        if angle is None:
            angle = self._direction
        x, y = self.position.dxy(b)
        return angle - atan2(y, x)

    def calc_position_with_bearing(self, b1: Position, b2: Position):
        possible_pos = self.position.intersection_of_beacon(b1, b2)
        if possible_pos is None:
            return None

        possible_pose11, possible_pose12 = self.possible_poses(b1, *possible_pos)
        possible_pose21, _ = self.possible_poses(b2, *possible_pos)

        if possible_pose11 == possible_pose21:
            return possible_pose11
        return possible_pose12

    def possible_poses(self, beacon, p1, p2):
        bear = self._bearing(beacon)  # use to calculate possible positions

        possible_pose1 = Pose.create_possible_pose(beacon, p1, bear)
        possible_pose2 = Pose.create_possible_pose(beacon, p2, bear)
        return possible_pose1, possible_pose2

    @staticmethod
    def create_possible_pose(beacon, position, bear):
        x, y = position.dxy(beacon)
        possible_pose2 = Pose(position, bear + atan2(y, x))
        return possible_pose2

    def update_pose(self, value: tuple[float, float, float]):
        x, y, d = value
        self._position.x += x
        self._position.y += y
        self._direction += d
