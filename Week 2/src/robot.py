from math import cos, pi, sin, atan, tan, atan2

import math
import numpy as np
import pygame
from position import Position
from pygame.surface import Surface
from sensor import Sensor
from velocity import Velocity
from box import Box
from line import Line
import shapely
from shapely.geometry import Point, LineString

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
        direction_label = myFont.render(str(self.direction), True, (0, 0, 0))
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
            if math.sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2) > 100:
                p.x, p.y = p_max.x, p_max.y

            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y),
                (p.x, p.y),
            )

            sensor_value = round(
                math.sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2)
            )
            sensor_display = myFont.render(str(sensor_value), True, (0, 0, 0))
            self.screen.blit(
                sensor_display,
                self.position.to_tuple_with_movement(
                    self.size * 3 * t_x - 0.5 * self.size,
                    self.size * 3 * t_y - 0.5 * self.size,
                ),
            )

    def get_angle(self, m1, m2):
        if m1 == float("inf") or m2 == 0:
            temp = m1
            m1 = m2
            m2 = temp
        # print(m1,m2)
        if m1 == m2:
            angle = 0
        elif m1 == -1 / m2:
            angle = pi / 2
        else:
            if m2 == float("inf"):
                angle = pi / 2 - atan(m1)
            else:
                angle = atan((m1 - m2) / (1 + m1 * m2))

        return angle

    def update_position(self, map: list[Line]):
        # v=abs(self.speed.left+self.speed.right)/2
        prev_x = self.position.x
        prev_y = self.position.y
        new_x = 0.0
        new_y = 0.0
        new_direction = 0.0

        if self.speed.is_straight():
            result = self._calc_update_straight()
        else:
            result = self._calc_update_in_turn()

        new_x, new_y, new_direction = result

        velocity = self._calc_velocity(prev_x, prev_y, new_x, new_y)

        for i, line in enumerate(map):
            collision_point = velocity.intersect_point_with_radius(line, self.size)
            if collision_point is not None:
                pygame.draw.circle(
                    self.screen, (255, 0, 0), collision_point.to_tuple(), 2
                )

            if line.distance_to(Position(new_x, new_y)) < self.size:
                # what to do if would collide
                p = velocity.intersect_point(line)
                if p is None:
                    raise Exception("This is not a valid update")
                # TODO(step 1): update until hit the wall
                # calc point at which the robot hits the wall
                collision_point = velocity.intersect_point_with_radius(line, self.size)
                if collision_point is None:
                    raise Exception("Can't be None")

                # TODO(step 2): update only in parallel direction
                # pygame.draw.circle(
                #     self.screen, (255, 0, 0), collision_point.to_tuple(), 2
                # )
                remaining_update = Position(new_x, new_y) - collision_point
                x, y = remaining_update.to_tuple()
                pygame.draw.circle(self.screen, (255, 0, 0), (300, 300), 1)
                pygame.draw.circle(
                    self.screen, (0, 0, 0), (x * 10 + 300, y * 10 + 300), 3
                )

                # TODO(step 2.1): update x and y so it is corresponded to the line we're hitting

                delta_line = Line(0, 0, x, y)

                alpha = line.radians()
                beta = self.direction - alpha
                q = sin(beta) * delta_line.len()
                u = sin(alpha) * q
                t = cos(alpha) * q
                if (self.direction - line.radians()) % pi * 2 in [pi / 2, 3 * pi / 2]:
                    new_x = prev_x
                    new_y = prev_y
                    break
                else:
                    angle = pi - line.radians()
                    self.position.x = prev_x
                    self.position.y = prev_y
                    self.position.x += self.speed.left * cos(angle + self.direction)
                    self.position.y += self.speed.left * sin(angle + self.direction)

                # pygame.draw.circle(self.screen, (255, 0, 0), (300, 300), 1)
                # pygame.draw.circle(
                #     self.screen, (0, 0, 0), (u * 10 + 300, t * 10 + 300), 3

                # beta = delta_line.radians() - line.radians()
                # x2 = cos(beta) * x - sin(beta) * y
                # y2 = sin(beta) * x + cos(beta) * y
                # new_x -= x2
                # new_y -= y2

                # TODO(step 2.2): update delta_line with new x and y

                # new_x, new_y = collision_point.to_tuple()
                print(remaining_update)
                # beneath line and line going down
                if line < self.position and line.gradient() > 0:
                    print(f"C1")
                    new_x += u
                    new_y -= t
                # beneath line and line going up
                elif line < self.position and line.gradient() < 0:
                    print(f"C2")
                    new_x -= u
                    new_y += t
                # above line and line going down
                elif line.gradient() > 0:
                    print(f"C3")
                    new_x += u
                    new_y -= t
                # above line and line going up
                else:
                    print(f"C4")
                    new_x += u
                    new_y -= t
                # print(
                #     f"{collision_point}, {self.position} {collision_point - self.position}"
                # )
                p_speed = cos(atan(line.gradient()) - self.direction)
                # get speed in parallel way

        self._set_position(new_x, new_y, new_direction)
        self._update_sensors()

    def _calc_velocity(self, prev_x, prev_y, new_x, new_y):
        if new_x == prev_x and new_y == prev_y:
            velocity = Line(
                prev_x,
                prev_y,
                prev_x + cos(self.direction),
                prev_y + sin(self.direction),
            )
        else:
            velocity = Line(prev_x, prev_y, new_x, new_y)
        return velocity

    def _calc_update_straight(self) -> tuple[float, float, float]:
        x = self.position.x + self.speed.left * cos(self.direction)
        y = self.position.y + self.speed.left * sin(self.direction)
        return x, y, self.direction

    def _calc_update_in_turn(self) -> tuple[float, float, float]:
        w = self._calc_w()
        R = self._calc_R()
        ICC = self._calc_ICC(R)
        a = self._calc_a(w)
        b = self._calc_b(ICC)
        c = self._calc_c(w, ICC)
        result = a.dot(b) + c
        return result[0][0], result[1][0], result[2][0]

    def _calc_c(self, w, ICC):
        return np.array([[ICC[0]], [ICC[1]], [w]])

    def _calc_b(self, ICC):
        return np.array(
            [
                [self.position.x - ICC[0]],
                [self.position.y - ICC[1]],
                [self.direction],
            ]
        )

    def _calc_a(self, w):
        return np.array([[cos(w), -sin(w), 0], [sin(w), cos(w), 0], [0, 0, 1]])

    def _calc_ICC(self, R):
        return [
            self.position.x - R * sin(self.direction),
            self.position.y + R * cos(self.direction),
        ]

    def _calc_w(self):
        return (self.speed.left - self.speed.right) / 20

    def _calc_R(self):
        return (
            20
            / 2
            * (self.speed.right + self.speed.left)
            / (self.speed.left - self.speed.right)
        )

    def _set_position(self, new_x, new_y, new_direction):
        self.position.x = new_x
        self.position.y = new_y
        self.direction = new_direction

    def _update_sensors(self):
        for s in self.sensors:
            s.direction = self.direction + s.offset
            s.position = self.position
