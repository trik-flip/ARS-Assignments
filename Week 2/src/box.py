from line import Line
import pygame
from pygame.surface import Surface


class Box:
    top: Line
    left: Line
    right: Line
    bottom: Line

    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self.top = Line(x1, y1, x2, y1)
        self.left = Line(x1, y1, x1, y2)
        self.right = Line(x2, y1, x2, y2)
        self.bottom = Line(x1, y2, x2, y2)

    def draw(self, screen: Surface, color=(0, 0, 0)):
        for line in self.lines():
            pygame.draw.line(screen, color, *line.to_tuple())

    def lines(self):
        return [self.top, self.right, self.bottom, self.left]
