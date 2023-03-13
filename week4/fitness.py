from numpy import average
from src.robby.robot import Robot


class fitness:
    @staticmethod
    def fitfunc(robot: Robot):
        """
        - [x] # of collisions
        - [x] area covered
        - [x] Average speed
        - [x] distance form starting point
        """

        avg = average(robot.speed_history)
        y = (((avg - 6) ** 2) * 5) - 100

        area_covered = 0
        been_here = [robot.history[0]]
        for pos in robot.history:
            if min([fitness._moved(*pos, *p) for p in been_here]) > robot.size:
                been_here.append(pos)
                area_covered += 1

        max_distance = max(
            [fitness._moved(*robot.history[0], *pos) for pos in robot.history]
        )
        collisions = robot.collision_count
        return -(max_distance * 3 - area_covered * 1) + (collisions * 100) + y

    @staticmethod
    def _moved(x, y, x2, y2):
        return ((x2 - x) ** 2 + (y2 - y) ** 2) ** 1 / 2
