from math import atan, cos, pi, sin, sqrt, tan

import numpy as np
import pygame
from pygame.surface import Surface

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


(width, height) = (1920, 1080)
STEP_SIZE = 0.001


class Position:
    x: float
    y: float

    def distance_to(self, other: object):
        assert isinstance(other, Position)
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x, self.y

    def to_tuple_with_movement(self, x, y):
        return self.x + x, self.y + y


class Line:
    start: Position
    end: Position

    def __init__(self, x1, y1, x2, y2) -> None:
        self.start = Position(x1, y1)
        self.end = Position(x2, y2)

    def to_tuple(self):
        return self.start.to_tuple(), self.end.to_tuple()

    def radians(self):
        return atan(self.gradient())

    def gradient(self):
        if self.start.x == self.end.x:
            return float("inf")
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def y_axis_intersect(self):
        return self.start.y - self.gradient() * self.start.x


class Box:
    top: Line
    left: Line
    right: Line
    bottom: Line

    def __init__(self, x1, y1, x2, y2) -> None:
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self.top = Line(x1, y1, x2, y1)
        self.left = Line(x1, y1, x1, y2)
        self.right = Line(x2, y1, x2, y2)
        self.bottom = Line(x1, y2, x2, y2)

    def draw(self, screen, color=BLACK):
        for line in self.lines():
            pygame.draw.line(screen, color, *line.to_tuple())

    def lines(self):
        return [self.top, self.right, self.bottom, self.left]


class Sensor:
    position: Position
    _direction: float
    direction: float

    def __init__(self, x, y, direction) -> None:
        self.position = Position(x, y)
        self._direction = direction
        self.direction = direction

    def does_intersect(self, line: Line):
        if line.gradient() == self.gradient():
            return False

        point = self.intersect(line)
        if point is None:
            return False

        going_right = 0 < cos(self.direction)
        going_up = 0 < sin(self.direction)

        if self.position.x > point[0] and going_right:
            return False
        if self.position.x < point[0] and not going_right:
            return False

        if self.position.y > point[1] and going_up:
            return False
        if self.position.y < point[1] and not going_up:
            return False

        small_x = min(line.start.x, line.end.x)
        big_x = max(line.start.x, line.end.x)
        if point[0] < small_x - 0.1 or point[0] > big_x + 0.1:
            return False

        small_y = min(line.start.y, line.end.y)
        big_y = max(line.start.y, line.end.y)
        if point[1] < small_y - 0.1 or point[1] > big_y + 0.1:
            return False

        return True

    def intersect(self, line: Line):
        l_g = line.gradient()
        s_g = self.gradient()
        if l_g == float("inf") or abs(l_g) > 1e15:
            x = line.start.x
            y = self._y_axis_intersect() + x * self.gradient()
            return x, y
        if s_g == float("inf") or abs(s_g) > 1e15:
            x = self.position.x
            y = line.y_axis_intersect() + x * line.gradient()
            return x, y
        if l_g == s_g:
            if line.y_axis_intersect() == self._y_axis_intersect():
                return self.position.to_tuple()
            return None
        y1 = self._y_axis_intersect()
        x = (line.y_axis_intersect() - y1) / (s_g - l_g)
        y = self.gradient() * x + y1
        return x, y

    def gradient(self):
        return tan(self.direction)

    def _y_axis_intersect(self):
        return self.position.y - self.position.x * self.gradient()


class Velocity:
    def __init__(self, left=0, right=0) -> None:
        self.left = left
        self.right = right

    left: float
    right: float

    def is_straight(self):
        return self.left == self.right

    def __eq__(self, __o: object) -> bool:
        assert isinstance(__o, Velocity)
        return self.left == __o.left and self.right == __o.right


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
            BLACK,
            self.position.to_tuple(),
            self.position.to_tuple_with_movement(t_x * self.size, t_y * self.size),
        )
        for sensor in self.sensors:
            t_x = cos(sensor.direction)
            t_y = sin(sensor.direction)
            x, y = None, None
            for line in lines:
                if sensor.does_intersect(line):
                    p = sensor.intersect(line)
                    if p is not None:
                        x, y = p
            if x is None:
                x, y = self.position.to_tuple_with_movement(
                    self.size * 3 * t_x, self.size * 3 * t_y
                )
            pygame.draw.line(
                self.screen,
                RED,
                self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y),
                (x, y),
            )

    def _update_position(self):
        if (self.speed.left + self.speed.right) == 0:
            return
        if self.speed.is_straight():
            self.position.x += self.speed.left * sin(self.direction)
            self.position.y += self.speed.left * cos(self.direction)
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


def main(background):
    running = True
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Robby Sim")
    screen.fill(background)

    robby = Robot(screen)
    box = Box(200, 200, 1700, 880)
    box.draw(screen)
    robby._draw(box.lines())
    pygame.display.update()
    assert robby.sensors[0].intersect(box.right) == (1700, 540)
    assert robby.sensors[7].intersect(box.top) == (
        371.1027254265813,
        200.00000000000003,
    )

    while running:
        screen.fill(background)
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Possible to use something like "last_pos = pygame.mouse.get_pos()"
                pass
            if event.type == pygame.QUIT:
                running = False
        key_event = pygame.key.get_pressed()
        if key_event[pygame.K_o]:
            robby.speed.right += STEP_SIZE
        if key_event[pygame.K_l]:
            robby.speed.right -= STEP_SIZE
        if key_event[pygame.K_w]:
            robby.speed.left += STEP_SIZE
        if key_event[pygame.K_s]:
            robby.speed.left -= STEP_SIZE

        robby._update_position()
        robby._draw(box.lines())
        box.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main(background=WHITE)
