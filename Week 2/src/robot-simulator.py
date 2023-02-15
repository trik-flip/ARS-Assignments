import pygame
from pygame.surface import Surface
from math import sin, cos, pi
import numpy as np
import time

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

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x, self.y

    def to_tuple_with_movement(self, x, y):
        return self.x + x, self.y + y


class Velocity:
    def __init__(self) -> None:
        self.left = 0
        self.right = 0

    left: float
    right: float


class Robot:
    def __init__(self, screen, size=20, color=(80,) * 3) -> None:
        self.position = Position(1920 / 2, 1080 / 2)
        self.speed = Velocity()
        self.direction = 0
        self.screen = screen
        self.size = size
        self.color = color

    position: Position
    speed: Velocity
    direction: float
    screen: Surface
    size: float
    color: tuple[int, int, int]

    def _clear(self, color):
        pygame.draw.circle(
            self.screen, color, self.position.to_tuple(), self.size * 1.5
        )

    def _draw(self):
        pygame.draw.circle(self.screen, self.color, self.position.to_tuple(), self.size)
        t_x = cos(self.direction)
        t_y = sin(self.direction)
        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            self.position.to_tuple(),
            self.position.to_tuple_with_movement(t_x * self.size, t_y * self.size),
        )

    def _update_position(self):
        if (self.speed.left + self.speed.right) == 0:
            return
        if self.speed.left == self.speed.right:
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


def main(background):
    running = True
    last_pos = [0, 0]
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Robby Sim")
    screen.fill(background)
    pygame.display.update()
    robby = Robot(screen)
    robby._draw()
    while running:
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                last_pos = pygame.mouse.get_pos()
                print(last_pos)
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

        robby._clear(background)
        robby._update_position()
        robby._draw()

        pygame.display.update()


if __name__ == "__main__":
    main(background=RED)
