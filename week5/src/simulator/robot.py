import numpy as np
from numpy.random import normal as random
import pygame
from math import cos, sin
from .pose import Pose
from .position import Position
from pygame.surface import Surface

pygame.font.init()
MY_FONT = pygame.font.SysFont("Times New Roman", 18)


class Robot:
    def __init__(
        self,
        size=20,
        color=(80,) * 3,
        position=(1920 / 2, 1080 / 2),
        speed=0,
        direction=0.0,
    ) -> None:
        """Create a robot which can drive and localize itself, we hope

        Args:
            size (int, optional): The radius of the robot. Defaults to 20.
            color (tuple[int,int,int], optional): the default color of the robot. Defaults to (80,)*3.
            position (tuple[float,float], optional): the current position. Defaults to (1920 / 2, 1080 / 2).
            speed (int, optional): the starting speed. Defaults to 0.
            direction (float, optional): the starting direction. Defaults to 0.0.
            max_steering_angle (float, optional): the max steering angle per frame executed. Defaults to 0.3.
        """
        self._prob_pose = Pose(
            Position.place_with_randomness(*position, k=100), direction
        )
        self._pose = Pose(Position(*position), direction)
        self.speed = speed
        self.size = size
        self.color = color
        self.history = []
        self.prob_history = []
        self.setup()

    def setup(self):
        self.steering_angle = 0

        self.A = np.identity(3)  # state to state transition
        self.C = np.identity(3)  # state to observation mapping
        self.R = np.identity(3) * 1e-5  # Pose prediction error
        self.Q = np.identity(3) * 1e-5  # ... prediction error
        self.__sigma = np.identity(3)  #

    @property
    def pose(self):
        return self._pose

    @pose.setter
    def pose(self, value):
        x, y, d = value
        self.pose.position = x, y
        self.pose._direction = d

    @property
    def prob_pose(self):
        return self._prob_pose

    @prob_pose.setter
    def prob_pose(self, value):
        x, y, d = value
        self.prob_pose.position = x, y
        self.prob_pose._direction = d

    _prob_pose: Pose
    _pose: Pose
    speed: float
    steering_angle: float
    max_steering_angle: float

    screen: Surface
    size: float
    color: tuple[int, int, int]

    __sigma: np.ndarray
    A: np.ndarray

    @property
    def B(self):
        x = cos(self._pose._direction)
        y = sin(self._pose._direction)
        return np.array([[x, 0], [y, 0], [0, 1]])

    @property
    def B_random(self):
        x = cos(self._prob_pose._direction)
        y = sin(self._prob_pose._direction)
        a = 1 + (random() - 0.5)
        return np.array([[x, 0.0], [y, 0.0], [0, a]])

    C: np.ndarray
    R: np.ndarray
    Q: np.ndarray

    @property
    def z(self):
        return self.C.dot(self._pose.array) + np.array([0, 0, 0])

    @property
    def z_prob(self):
        return self.C.dot(self._prob_pose.array) + np.array([0, 0, 0])

    @property
    def mu(self):
        return self._pose.array

    @property
    def mu_prob(self):
        return self._prob_pose.array

    @property
    def u(self):
        sa = self.steering_angle

        return np.array([self.speed, sa])

    @u.setter
    def u(self, _val):
        self.steering_angle = 0

    @property
    def sigma(self):
        return self.__sigma

    @property
    def mu_pred(self):
        return self.A.dot(self.mu) + self.B.dot(self.u)

    @property
    def mu_pred_random(self):
        return self.A.dot(self.mu_prob) + self.B_random.dot(self.u) * (
            1 + (8 * random() / 10) - 0.2
        )

    @property
    def sigma_pred(self):
        return self.A.dot(self.sigma).dot(self.A.T) + self.R

    @property
    def k_correction(self):
        return self.sigma_pred.dot(self.C.T).dot(
            np.linalg.inv(self.C.dot(self.sigma_pred).dot(self.C.T) + self.Q)
        )

    def update_mu(self):
        return self.mu_pred + self.k_correction.dot(self.z - self.C.dot(self.mu_pred))

    def update_mu_random(self):
        return self.mu_pred_random + self.k_correction.dot(
            self.z_prob - self.C.dot(self.mu_pred_random)
        )

    def update_sigma(self):
        return (np.identity(3) - self.k_correction.dot(self.C)).dot(self.sigma_pred)

    def update(self, beacons: list[Position]):
        self.history.append(self.pose.array)
        self.prob_history.append(self.prob_pose.array)

        self.pose = self.update_mu()
        self.prob_pose = self.update_mu_random()
        if len(beacons) >= 3:
            for i in range(len(beacons) - 2):
                b1, b2, b3 = beacons[i : i + 3]

                bp = self._pose.position.triangulate_with_beacons(b1, b2, b3)
                if bp is not None:
                    self._prob_pose.position = self._pose.position.xy
        self.__sigma = self.update_sigma()
        self.u = "reset"

    def draw(self, screen):
        draw_robot(
            screen, self.size, self.pose.position, self.pose._direction, self.color
        )
        draw_robot(
            screen,
            self.size,
            self.prob_pose.position,
            self.prob_pose._direction,
            (255, 0, 0),
        )


def draw_robot(
    screen,
    size: float,
    position: Position,
    direction: float,
    color: tuple[int, int, int],
):
    pygame.draw.circle(
        screen,
        color,
        position.xy,
        size,
    )
    looking_line = position.add_polar(size, direction)
    pygame.draw.line(
        screen,
        (0, 0, 0),
        position.xy,
        looking_line.xy,
    )
