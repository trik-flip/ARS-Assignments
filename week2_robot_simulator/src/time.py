import pygame
BLACK = (255,255,255)

class Time:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 20)
        self.text = self.font.render(str(self.clock.get_fps()), True, BLACK)
 
    def render(self, display):
        self.text = self.font.render(str(round(self.clock.get_fps(),2)), True, BLACK)
        display.blit(self.text, (200, 150))