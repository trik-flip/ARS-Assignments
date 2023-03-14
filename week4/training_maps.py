import pygame
from src.robby.box import Box
from src.robby.line import Line

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

STEP_SIZE = 0.1


(width, height) = (1900, 1060)

background = WHITE
running = True
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

##### MAP 1 #######

box1 = Box(200, 200, 1700, 880)
box1.draw(screen)
box2 = Box(300,300, 1600, 780)
box2.draw(screen)
game_map = box1.lines() + box2.lines()

##################


##### MAP 2 #######

# box1 = Box(200, 200, 1700, 880)
# box1.draw(screen)

# point1 = 400, 400
# point2 = 400, 880 - 100
# point3 = 1500 - 200, 860 - 200
# point4 = 1500 - 50, 860 - 50

# line1 = Line(*point1, *point2)
# line2 = Line(*point1, *point3)
# line3 = Line(*point2, *point4)
# line4 = Line(*point3, *point4)


# pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line4.to_tuple())



##################






while running:
    pygame.display.update()
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            running = False


