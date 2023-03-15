from src.robby.box import Box
from src.robby.line import Line


def triangle():
    point1 = 350, 350
    point2 = 350, 880 - 150
    point3 = 1700 - 150, 880 - 150

    line1 = Line(*point1, *point2)
    line2 = Line(*point2, *point3)
    line3 = Line(*point1, *point3)
    return [line1, line2, line3]


def double_trapezoid():
    point1 = 200, 200
    point2 = 200, 880
    point3 = 1700, 200 + 150
    point4 = 1700, 880 - 150

    line1 = Line(*point1, *point2)
    line2 = Line(*point1, *point3)
    line3 = Line(*point2, *point4)
    line4 = Line(*point3, *point4)

    game_map = [line1, line2, line3, line4]

    point1 = 350, 350
    point2 = 350, 880 - 150
    point3 = 1700 - 150, 200 + 150 + 100
    point4 = 1700 - 150, 880 - 150 - 100

    line1 = Line(*point1, *point2)
    line2 = Line(*point1, *point3)
    line3 = Line(*point2, *point4)
    line4 = Line(*point3, *point4)

    game_map = game_map + [line1, line2, line3, line4]
    return game_map


def room():
    box1 = Box(200, 200, 1700, 880)
    box2 = Box(350, 350, 500, 500)
    box3 = Box(1500 / 2, 880, 1500 / 2 + 100, 500)
    box4 = Box(1500, 550, 1200, 300)
    game_map = box1.lines() + box2.lines() + box3.lines() + box4.lines()
    return game_map


def valley_map():
    box1 = Box(200, 200, 1700, 880)

    game_map = box1.lines()

    point1 = 200, 880
    point2 = 750, 880
    point3 = 500, 400

    line1 = Line(*point1, *point2)
    line2 = Line(*point2, *point3)
    line3 = Line(*point1, *point3)

    game_map = game_map + [line1, line2, line3]

    point1 = 1700 - 550, 880
    point2 = 1700, 880
    point3 = 1450, 400

    line1 = Line(*point1, *point2)
    line2 = Line(*point2, *point3)
    line3 = Line(*point1, *point3)

    game_map = game_map + [line1, line2, line3]

    point1 = 750, 200
    point2 = 1700 - 550, 200
    point3 = 950, 700

    line1 = Line(*point1, *point2)
    line2 = Line(*point2, *point3)
    line3 = Line(*point1, *point3)

    game_map = game_map + [line1, line2, line3]
    return game_map
