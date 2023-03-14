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
background = WHITE
background = WHITE
running = True
pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Robby Sim")
screen.fill(background)

# ##### Double trapezoid #######

# point1 = 200, 200
# point2 = 200, 880 
# point3 = 1700, 200 + 150
# point4 = 1700, 880 - 150

# line1 = Line(*point1, *point2)
# line2 = Line(*point1, *point3)
# line3 = Line(*point2, *point4)
# line4 = Line(*point3, *point4)


# pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line4.to_tuple())

# game_map = [line1,line2,line3,line4]

# point1 = 350, 350
# point2 = 350, 880 - 150 
# point3 = 1700 - 150, 200 + 150 + 100
# point4 = 1700-150, 880 - 150 -100

# line1 = Line(*point1, *point2)
# line2 = Line(*point1, *point3)
# line3 = Line(*point2, *point4)
# line4 = Line(*point3, *point4)


# pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())
# pygame.draw.line(screen, (0, 0, 0), *line4.to_tuple())

# game_map = game_map+[line1,line2,line3,line4]
##################



##### Room ##########

# box1 = Box(200, 200, 1700, 880)
# box1.draw(screen)
# box2 = Box(350,350, 500, 500)
# box2.draw(screen)
# box3 = Box(1500/2,880, 1500/2+100, 500)
# box3.draw(screen)
# box4 = Box(1500,550, 1200, 300)
# box4.draw(screen)
# game_map = box1.lines() + box2.lines() + box3.lines() +box4.lines()

##################



##### Valley Map ##########

box1 = Box(200, 200, 1700, 880)
box1.draw(screen)

game_map= box1.lines()

point1 = 200, 880
point2 = 750, 880
point3 = 500,400

line1 = Line(*point1, *point2)
line2 = Line(*point2, *point3)
line3 = Line(*point1, *point3)

pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())

game_map = game_map+[line1,line2,line3]


point1 = 1700-550, 880
point2 = 1700, 880
point3 = 1450,400

line1 = Line(*point1, *point2)
line2 = Line(*point2, *point3)
line3 = Line(*point1, *point3)

pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())

game_map = game_map+[line1,line2,line3]



point1 = 750, 200
point2 = 1700-550, 200
point3 = 950,700

line1 = Line(*point1, *point2)
line2 = Line(*point2, *point3)
line3 = Line(*point1, *point3)

pygame.draw.line(screen, (0, 0, 0), *line1.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line2.to_tuple())
pygame.draw.line(screen, (0, 0, 0), *line3.to_tuple())

game_map = game_map+[line1,line2,line3]




##################












while running:
    pygame.display.update()
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            running = False


