from math import atan, cos, pi, sin, sqrt

import numpy as np
import pygame
from .box import Box
from .line import Line
from .position import Position
from pygame.surface import Surface
from .sensor import Sensor
from .velocity import Velocity

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
        self.to_draw = []
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

    to_draw: list
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
                if sensor.intersects(line):
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
            sensor.value = sensor_value
            sensor_display = myFont.render(str(sensor_value), True, (0, 0, 0))
            self.screen.blit(
                sensor_display,
                self.position.to_tuple_with_movement(
                    self.size * 3 * t_x - 0.5 * self.size,
                    self.size * 3 * t_y - 0.5 * self.size,
                ),
            )
        for drawing in self.to_draw:
            drawing()
        self.to_draw = []

    def update_position(self, lines: list[Line]):
        x, y, direction = self.__calc_update()
        if self.current_pose(x, y, direction):
            return
        velocity = self.__calc_velocity(x, y)
        # for line in sorted(lines, key=lambda l: velocity.intersects(l)):
        for wall in lines:
            if wall.distance_to(new_pos := Position(x, y)) <= (
                self.size
            ) or velocity.intersects(wall):
                collision_point = velocity.intersect_point_with_radius(wall, self.size)
                remaining_update = new_pos - collision_point

                residual_force = Line(0, 0, *remaining_update.to_tuple())
                # Source: https://matthew-brett.github.io/teaching/rotation_2d.html
                # Image showing the x and y delta of the velocity parallel to the wall

                x_speed, y_speed = self.calc_force_on_wall(wall, residual_force)

                x_speed, y_speed = self.account_for_backwards_driving(x_speed, y_speed)

                x += x_speed
                y -= y_speed
                velocity = self.__calc_velocity(x, y)
                print(velocity)

        if self.current_pose(x, y, direction):
            return

        for wall in lines:
            if wall.distance_to(Position(x, y)) < self.size:
                print("hitting")
        new_pos = lambda: pygame.draw.line(
            self.screen, (0, 255, 0), *(velocity * 10).to_tuple()
        )
        self.to_draw.append(new_pos)
        if not any(map(lambda l: l.intersects(velocity), lines)):
            self.set_position(x, y, direction)
            self.__update_sensors()

    def account_for_backwards_driving(self, u, t):
        driving_backwards = self.speed.left + self.speed.right < 0
        if driving_backwards:
            u, t = -u, -t
        return u, t

    def calc_force_on_wall(self, line, delta_line):
        alpha = line.radians()
        beta = self.direction - alpha
        q = sin(beta) * delta_line.len()
        u = sin(alpha) * q
        t = cos(alpha) * q
        return u, t

    def current_pose(self, x, y, direction):
        return (
            x == self.position.x
            and y == self.position.y
            and direction == self.direction
        )

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
        return Line(*self.position.to_tuple(), x, y)

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
