import itertools
from math import cos, sin

import numpy as np
import pygame
from numpy.random import normal as random
from pygame.surface import Surface

from .pose import Pose
from .position import Position

pygame.font.init()
MY_FONT = pygame.font.SysFont("Times New Roman", 18)


class Robot:
    def __init__(
        self,
        *,
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
        self.pose = Pose(Position(*position), direction)
        self.mu = Pose(Position.place_with_noise(*position, k=100), direction).array
        self.speed = speed
        self.size = size
        self.color = color
        self.history = []
        self.prob_history = []
        self.setup()

    def setup(self):
        self.steering_angle = 0

        self.C = np.identity(3)  # state to observation mapping
        self.R = np.identity(3) * 1e-5  # Pose prediction error
        self.Q = np.identity(3) * 1e-5  # ... prediction error
        self.__sigma = np.identity(3)  #

    speed: float
    steering_angle: float
    max_steering_angle: float

    screen: Surface
    size: float
    color: tuple[int, int, int]

    mu: np.ndarray
    __sigma: np.ndarray

    @property
    def B(self):
        x = cos(self.mu[2])
        y = sin(self.mu[2])
        return np.array([[x, 0], [y, 0], [0, 1]])

    C: np.ndarray
    R: np.ndarray
    Q: np.ndarray

    @property
    def z(self):
        return self.C.dot(self.mu) + np.array([random(), random(), random()])

    @property
    def u(self):
        sa = self.steering_angle
        return np.array([self.speed, sa])

    @property
    def noisy_u(self):
        sa = self.steering_angle * random(loc=1, scale=1)
        speed = self.speed * random(loc=1, scale=0.8)
        return np.array([speed, sa])

    @property
    def mu_pred(self):
        return self.mu + self.B.dot(self.noisy_u)

    @property
    def sigma_pred(self):
        return self.__sigma + self.R

    @property
    def k_correction(self):
        return self.sigma_pred.dot(self.C.T).dot(
            np.linalg.inv(self.C.dot(self.sigma_pred).dot(self.C.T) + self.Q)
        )

    @property
    def update_mu(self):
        return self.k_correction.dot(self.z - self.C.dot(self.mu_pred))

    def update_sigma(self):
        return (np.identity(3) - self.k_correction.dot(self.C)).dot(self.sigma_pred)

    def update(self, beacons: list[Position]):
        self._save_history()
        # Prediction
        self._update()

        self.mu = self.mu_pred
        self.__sigma = self.sigma_pred

        # NOTE: Maybe check first if there are at least 2 beacons
        # When a localization is done we can break and add the correction step
        for b1, b2 in itertools.combinations(beacons, 2):
            pos_p = self.pose.calc_position_with_bearing(b1, b2)
            if pos_p is not None:
                self.mu = pos_p.array
                pass
                # TODO: the correction step
                # draw_robot(screen, 30, pos_p.position, pos_p._direction, (0, 200, 0))
                break
        self.steering_angle = 0

    def _update(self):
        x = cos(self.pose._direction)
        y = sin(self.pose._direction)
        local_b = np.array([[x, 0], [y, 0], [0, 1]])
        self.pose.update_pose(local_b.dot(self.u))

    def _save_history(self):
        self.history.append(self.pose.array)
        self.prob_history.append(self.mu)

    def draw(self, screen):
        draw_pose(screen, self.pose, self.size, self.color)
        draw_pose(
            screen,
            self.mu,
            self.size,
            (255, 0, 0),
        )


def draw_pose(
    screen,
    pose: Pose | tuple[float, float, float],
    size: float,
    color: tuple[int, int, int],
):
    if isinstance(pose, Pose):
        draw_robot_circle(screen, size, pose.position, pose._direction, color)
    else:
        draw_robot_circle(screen, size, pose[:2], pose[2], color)


def draw_robot_circle(
    screen,
    size: float,
    position: Position | tuple[float, float],
    direction: float,
    color: tuple[int, int, int],
):
    if not isinstance(position, Position):
        position = Position(*position)
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
