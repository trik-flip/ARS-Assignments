from hashlib import new
import numpy as np
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
        max_steering_angle=0.3,
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
        self._pose = Pose(Position(*position), direction)
        self.speed = speed
        self.size = size
        self.color = color
        self.max_steering_angle = max_steering_angle

        self.setup()

    def setup(self):
        self.A = np.identity(3)
        self.C = np.identity(3)
        self.steering_angle = 0
        self.R = np.identity(3) * 1e-5
        self.Q = np.identity(3) * 1e-5
        self.__sigma = np.identity(3)

    @property
    def pose(self):
        return self._pose

    @pose.setter
    def pose(self, value):
        x, y, d = value
        self.pose.position = x, y
        self.pose._direction = d

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
        return np.array(
            [[cos(self._pose._direction), 0], [sin(self._pose._direction), 0], [0, 1]]
        )

    C: np.ndarray
    R: np.ndarray
    Q: np.ndarray

    @property
    def z(self):
        return self.C.dot(self._pose.array) + np.array([0, 0, 0])

    @property
    def mu(self):
        return self._pose.array

    @property
    def u(self):
        sa = self.steering_angle
        self.steering_angle = 0
        return np.array([self.speed, sa])

    @property
    def sigma(self):
        return self.__sigma

    @property
    def mu_pred(self):
        return self.A.dot(self.mu) + self.B.dot(self.u)

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

    def update_sigma(self):
        return (np.identity(3) - self.k_correction.dot(self.C)).dot(self.sigma_pred)

    def update(self):
        self.pose = self.update_mu()
        self.__sigma = self.update_sigma()

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self._pose._position.x, self._pose._position.y),
            self.size,
        )
        pygame.draw.line(
            screen,
            (0, 0, 0),
            self.pose.position.xy,
            (
                self.pose.position
                + Position.create_polar(self.size, self.pose._direction)
            ).xy,
        )
