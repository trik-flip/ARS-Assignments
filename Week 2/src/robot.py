from math import cos, pi, sin

import numpy as np
import pygame
from position import Position
from pygame.surface import Surface
from sensor import Sensor
from velocity import Velocity


class Robot:
    def __init__(
        self,
        screen,
        size=20,
        color=(80,) * 3,
        position=(1920 / 2, 1080 / 2),
        speed=(0, 0),
        direction=0.0,
        sensors=12,
    ) -> None:
        self.position = Position(*position)
        self.speed = Velocity(*speed)
        self.direction = direction
        self.screen = screen
        self.size = size
        self.color = color
        self.sensors = [
            Sensor(*self.position.to_tuple(), (pi * 2 / sensors) * i)
            for i in range(sensors)
        ]

    sensors: list[Sensor]
    position: Position
    speed: Velocity
    direction: float
    screen: Surface
    size: float
    color: tuple[int, int, int]

    def _clear(self, color):
        pygame.draw.circle(self.screen, color, self.position.to_tuple(), self.size * 5)

    def _draw(self, lines=[]):
        pygame.draw.circle(self.screen, self.color, self.position.to_tuple(), self.size)
        t_x = cos(self.direction)
        t_y = sin(self.direction)

        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            self.position.to_tuple(),
            self.position.to_tuple_with_movement(t_x * self.size, t_y * self.size),
        )
        for sensor in self.sensors:
            t_x = cos(sensor.direction)
            t_y = sin(sensor.direction)

            p = None
            distance = float("inf")
            for line in lines:
                if sensor.is_intersect(line):
                    temp_p = sensor.intersect_point(line)
                    if (distance_to := self.position.distance_to(temp_p)) < distance:
                        distance = distance_to
                        p = temp_p
            if p is None:
                x, y = self.position.to_tuple_with_movement(
                    self.size * 3 * t_x, self.size * 3 * t_y
                )
                p = Position(x, y)
            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y),
                (p.x, p.y),
            )

    def _update_position(self):
        if (self.speed.left + self.speed.right) == 0:
            return
        if self.speed.is_straight():
            self.position.x += self.speed.left * cos(self.direction)
            self.position.y += self.speed.left * sin(self.direction)
            for s in self.sensors:
                s.position = self.position
        else:
            R = (
                20
                / 2
                * (self.speed.right + self.speed.left)
                / (self.speed.left - self.speed.right)
            )

            w = (self.speed.left - self.speed.right) / 20

            ICC = [
                self.position.x - R * sin(self.direction),
                self.position.y + R * cos(self.direction),
            ]

            a = np.array([[cos(w), -sin(w), 0], [sin(w), cos(w), 0], [0, 0, 1]])

            b = np.array(
                [
                    [self.position.x - ICC[0]],
                    [self.position.y - ICC[1]],
                    [self.direction],
                ]
            )

            c = np.array([[ICC[0]], [ICC[1]], [w]])

            result = a.dot(b) + c

            self.position.x = result[0][0]
            self.position.y = result[1][0]
            self.direction = result[2][0]
            for s in self.sensors:
                s.direction = self.direction + s._direction
                s.position = self.position
