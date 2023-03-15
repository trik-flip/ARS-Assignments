from src.robby.box import Box
from src.robby.line import Line


def map1():
    box1 = Box(200, 200, 1700, 880)
    box2 = Box(300, 300, 1600, 780)
    game_map = box1.lines() + box2.lines()
    return game_map


def map2():
    point1 = 400, 400
    point2 = 400, 880 - 100
    point3 = 1500 - 200, 860 - 200
    point4 = 1500 - 50, 860 - 50

    line1 = Line(*point1, *point2)
    line2 = Line(*point1, *point3)
    line3 = Line(*point2, *point4)
    line4 = Line(*point3, *point4)
    game_map = [line1, line2, line3, line4]
    return game_map
