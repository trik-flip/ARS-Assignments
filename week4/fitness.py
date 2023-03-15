from numpy import average
from src.robby.robot import Robot
import pygame
from pygame.surface import Surface


class fitness:
    @staticmethod
    def calc(robot: Robot):
        distance = -fitness.__calc_distance_traveled_from_origin(robot)
        area_covered = -robot.area_covered()
        double_area = fitness.__calc_area_double_covered(robot)
        collisions = robot.collision_count
        avg_speed = fitness.__calc_average_speed(robot)

        return (
            (distance * 0)
            + (area_covered * 1)
            + (collisions * 0)
            + (avg_speed * 0)
            + (double_area * 0)
        )

    @staticmethod
    def __calc_average_speed(robot):
        avg = average(robot.speed_history)
        y = (((avg - 6) ** 2) * 5) - 100
        return y

    @staticmethod
    def __calc_collisions(robot):
        collisions = robot.collision_count
        return collisions

    @staticmethod
    def __calc_distance_traveled_from_origin(robot):
        max_distance = max(
            [
                fitness.__distance_between_points(*robot.history[0], *pos)
                for pos in robot.history
            ]
        )

        return max_distance

    @staticmethod
    def __calc_area_covered(robot):
        been_here = [robot.history[0]]
        for pos in robot.history:
            add = True
            for recorded_pos in been_here:
                if fitness.__distance_between_points(*pos, *recorded_pos) < robot.size:
                    add = False
            if add:
                been_here.append(pos)
        return len(been_here)

    @staticmethod
    def __calc_area_double_covered(robot):
        counter = 0
        been_here = [robot.history[0]]
        for pos in robot.history:
            add = True
            for recorded_pos in been_here:
                if fitness.__distance_between_points(*pos, *recorded_pos) < robot.size:
                    add = False
            if add:
                been_here.append(pos)
            else:
                counter += 1
        return counter

    @staticmethod
    def __distance_between_points(x, y, x2, y2):
        return ((x2 - x) ** 2 + (y2 - y) ** 2) ** (1 / 2)
