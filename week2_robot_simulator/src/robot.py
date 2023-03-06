from math import atan, cos, pi, sin, sqrt

import numpy as np
import pygame
from box import Box
from line import Line
from position import Position
from pygame.surface import Surface
from sensor import Sensor
from velocity import Velocity

pygame.font.init()
myFont = pygame.font.SysFont("Times New Roman", 18)


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
        box_tuple=Box(200, 200, 1700, 880),
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
        self.box_tuple = box_tuple

    sensors: list[Sensor]
    position: Position
    speed: Velocity
    direction: float
    screen: Surface
    size: float
    color: tuple[int, int, int]
    box_tuple = tuple[int, int, int, int]

    def draw(self, lines=[]):
        pygame.draw.circle(self.screen, self.color, self.position.to_tuple(), self.size)
        t_x = cos(self.direction)
        t_y = sin(self.direction)

        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            self.position.to_tuple(),
            self.position.to_tuple_with_movement(t_x * self.size, t_y * self.size),
        )
        speed_label1 = myFont.render(str(round(self.speed.left * 10)), True, (0, 0, 0))
        speed_label2 = myFont.render(str(round(self.speed.right * 10)), True, (0, 0, 0))
        self.screen.blit(
            speed_label1,
            self.position.to_tuple_with_movement(
                t_x - 0.3 * self.size, t_y - self.size
            ),
        )
        self.screen.blit(
            speed_label2,
            self.position.to_tuple_with_movement(t_x - 0.3 * self.size, t_y),
        )

        for sensor in self.sensors:
            t_x = cos(sensor.direction)
            t_y = sin(sensor.direction)

            p = None
            distance = float("inf")

            for line in lines:
                if sensor.does_intersect(line):
                    temp_p = sensor.intersect_point(line)
                    if (distance_to := self.position.distance_to(temp_p)) < distance:
                        distance = distance_to
                        p = temp_p
            if p is None:
                continue
            x, y = self.position.to_tuple_with_movement(
                self.size * 6 * t_x, self.size * 6 * t_y
            )

            p_max = Position(x, y)
            start = self.position.to_tuple_with_movement(
                self.size * t_x, self.size * t_y
            )
            if sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2) > 100:
                p.x, p.y = p_max.x, p_max.y

            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y),
                (p.x, p.y),
            )

            sensor_value = round(sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2))
            sensor_display = myFont.render(str(sensor_value), True, (0, 0, 0))
            self.screen.blit(
                sensor_display,
                self.position.to_tuple_with_movement(
                    self.size * 3 * t_x - 0.5 * self.size,
                    self.size * 3 * t_y - 0.5 * self.size,
                ),
            )

    def update_position(self, lines: list[Line]):
        x, y, direction = self.__calc_update()

        velocity = self.__calc_velocity(x, y)

        for line in lines:
            if line.distance_to(Position(x, y)) <= self.size:
                collision_point = velocity.intersect_point_with_radius(line, self.size)

                remaining_update = Position(x, y) - collision_point
                delta_line = Line(0, 0, *remaining_update.to_tuple())

                # Source: https://matthew-brett.github.io/teaching/rotation_2d.html
                # Image showing the x and y delta of the velocity parallel to the wall

                alpha = line.radians()
                beta = self.direction - alpha
                q = sin(beta) * delta_line.len()
                u = sin(alpha) * q
                t = cos(alpha) * q
                swap = self.speed.left + self.speed.right < 0
                if not swap:
                    x += u
                    y -= t
                else:
                    x -= u
                    y += t

        collision_line = Line(*self.position.to_tuple(), x, y)
        update = True

        for line in lines:
            if (
                collision_line.does_intersect(line)
                or line.distance_to(Position(x, y)) <= self.size
            ) and collision_line.len() <= 1e-10:
                update = False

        if self.speed.left == -self.speed.right:
            update = True

        if update:
            self.set_position(x, y, direction)
            self.__update_sensors()

    def __calc_update(self):
        if self.speed.is_straight():
            return self.__calc_straight_update()
        return self.__calc_circle_update()

    def __calc_velocity(self, x, y):
        if x == self.position.x and y == self.position.y:
            return Line(
                self.position.x,
                self.position.y,
                self.position.x + cos(self.direction),
                self.position.y + sin(self.direction),
            )
        return Line(self.position.x, self.position.y, x, y)

    def __calc_straight_update(self) -> tuple[float, float, float]:
        x = self.position.x + self.speed.left * cos(self.direction)
        y = self.position.y + self.speed.left * sin(self.direction)
        return x, y, self.direction

    def __calc_circle_update(self) -> tuple[float, float, float]:
        w = self.__calc_w()
        R = self.__calc_r()
        ICC = self.__calc_icc(R)

        a = self.__calc_a(w)
        b = self.__calc_b(ICC)
        c = self.__calc_c(w, ICC)

        result = a.dot(b) + c
        return result[0][0], result[1][0], result[2][0]

    def __calc_c(self, w, icc: list[float]):
        return np.array([[icc[0]], [icc[1]], [w]])

    def __calc_b(self, icc: list[float]):
        return np.array(
            [
                [self.position.x - icc[0]],
                [self.position.y - icc[1]],
                [self.direction],
            ]
        )

    def __calc_a(self, w):
        return np.array([[cos(w), -sin(w), 0], [sin(w), cos(w), 0], [0, 0, 1]])

    def __calc_icc(self, r: float):
        return [
            self.position.x - r * sin(self.direction),
            self.position.y + r * cos(self.direction),
        ]

    def __calc_w(self):
        return (self.speed.left - self.speed.right) / 20

    def __calc_r(self):
        return (
            20
            / 2
            * (self.speed.right + self.speed.left)
            / (self.speed.left - self.speed.right)
        )

    def set_position(self, x: float, y: float, direction: float | None = None):
        self.position.x = x
        self.position.y = y
        if direction is not None:
            self.direction = direction

    def __update_sensors(self):
        for s in self.sensors:
            s.direction = self.direction + s.offset
            s.position = self.position
