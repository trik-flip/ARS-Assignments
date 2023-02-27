from math import cos, pi, sin ,atan,tan,atan2

import math
import numpy as np
import pygame
from position import Position
from pygame.surface import Surface
from sensor import Sensor
from velocity import Velocity
from box import Box
from line import Line
import shapely
from shapely.geometry import Point, LineString

pygame.font.init()
myFont = pygame.font.SysFont("Times New Roman", 18)
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
        box_tuple=Box(200,200,1700,880)
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
        self.box_tuple=box_tuple
    sensors: list[Sensor]
    position: Position
    speed: Velocity
    direction: float
    screen: Surface
    size: float
    color: tuple[int, int, int]
    box_tuple = tuple[int, int, int, int]
    def _clear(self, color):
        pygame.draw.circle(self.screen, color, self.position.to_tuple(), self.size * 5)

    def _draw(self, lines=[]):
        pygame.draw.circle(self.screen, self.color, self.position.to_tuple(), self.size)
        t_x = cos(self.direction)
        t_y = sin(self.direction)

        pygame.draw.line(
            self.screen,
            (0, 0, 0),
            self.position.to_tuple(),
            self.position.to_tuple_with_movement(t_x * self.size, t_y * self.size),
        )
        direction_label=myFont.render(str(self.direction), 1, (0, 0, 0))
        speed_label1 = myFont.render(str(round(self.speed.left*10)), 1, (0, 0, 0))
        speed_label2 = myFont.render(str(round(self.speed.right*10)), 1, (0, 0, 0))
        self.screen.blit(speed_label1, self.position.to_tuple_with_movement(t_x - .3 * self.size, t_y - self.size))
        self.screen.blit(speed_label2, self.position.to_tuple_with_movement(t_x - .3 * self.size, t_y))

        for sensor in self.sensors:
            t_x = cos(sensor.direction)
            t_y = sin(sensor.direction)

            p = None
            distance = float("inf")

            for line in lines:
                if sensor.is_intersect(line):
                    temp_p = sensor.intersect_point(line)
                    if (distance_to := self.position.distance_to(temp_p)) < distance:
                        distance = distance_to
                        p = temp_p
            # if p is None:
            x, y = self.position.to_tuple_with_movement(
                self.size * 6 * t_x, self.size * 6 * t_y
            )

            p_max = Position(x, y)
            start=self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y)
            if math.sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2) > 100:
                p.x, p.y = p_max.x, p_max.y
            # p.x, p.y = min(p_max.x, p.x), min(p_max.y, p.y)
            #
            # if(math.sqrt((self.size*t_x - p.x) ** 2 + (self.size*t_y - p.y) ** 2))<5:
            #     p.x,p.y=p_max.x,p_max.y

            pygame.draw.line(
                self.screen,
                (255, 0, 0),
                self.position.to_tuple_with_movement(self.size * t_x, self.size * t_y),
                (p.x, p.y),
            )

            sensor_val=round(math.sqrt((start[0] - p.x) ** 2 + (start[1] - p.y) ** 2))
            sensor_disp=myFont.render(str(sensor_val), 1, (0,0,0))
            self.screen.blit(sensor_disp, self.position.to_tuple_with_movement(self.size*3 * t_x - .5 * self.size, self.size*3 * t_y - .5 * self.size))

    def get_angle(self, m1, m2):
        if (m1 == float("inf") or m2 == 0):
            temp = m1
            m1 = m2
            m2 = temp
        # print(m1,m2)
        if (m1 == m2):
            angle = 0
        elif (m1 == -1 / m2):
            angle = pi / 2
        else:
            if (m2 == float("inf")):
                angle = pi / 2 - atan(m1)
            else:
                angle = atan((m1 - m2) / (1 + m1 * m2))

        return angle

    def _update_position(self, map: list[Line]):
        v=(self.speed.left+self.speed.right)/2
        # l=self.speed.left
        # r=self.speed.right
        prev_x = self.position.x
        prev_y = self.position.y
        # collision=False

        if (self.speed.left + self.speed.right) == 0:
            self.position.x = self.position.x
            self.position.y = self.position.y
        if self.speed.is_straight():
            self.position.x += self.speed.left * cos(self.direction)
            self.position.y += self.speed.left * sin(self.direction)
            if (self.position.x > (self.box_tuple.right.start.x - self.size)) or (
                self.position.x
            ) < (self.box_tuple.left.start.x + self.size):
                self.position.x = prev_x
            if (self.position.y > (self.box_tuple.bottom.start.y - self.size)) or (
                self.position.y
            ) < (self.box_tuple.top.start.y + self.size):
                self.position.y = prev_y
            for i, line in enumerate(map):
                if line.distance_to(self.position) < self.size:
                    print("collision")
                    collision = True
                else:
                    collision = False
                if (collision == True):
                    # self.position.x = prev_x
                    # self.position.y = prev_y
                    angle_intersection = self.get_angle(tan(self.direction), line.gradient())
                    if round(angle_intersection,2)==round(pi/2,2) or round(angle_intersection,2)== round(3*pi/2,2):
                        # print("working")
                        self.position.x = prev_x
                        self.position.y = prev_y
                    else:
                        line_angle=pi-atan(line.gradient())
                        self.position.x = prev_x
                        self.position.y = prev_y
                        self.position.x += (self.speed.left * cos(line_angle+self.direction))
                        self.position.y += (self.speed.left * sin(line_angle+self.direction))
                        print(angle_intersection,pi/2)
                        collision = False
                    # self.speed.left = v_component * self.speed.left / (self.speed.left + self.speed.right)   # case for inertia considered
                    # self.speed.right = v_component * self.speed.right / (self.speed.left + self.speed.right)

                    collision = False
            for s in self.sensors:
                s.position = self.position
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
            if((self.position.x> (self.box_tuple.right.start.x-self.size)) or (self.position.x)<(self.box_tuple.left.start.x+self.size)):
                self.position.x=prev_x
            if ((self.position.y > (self.box_tuple.bottom.start.y - self.size)) or (self.position.y) < (self.box_tuple.top.start.y + self.size)):
                self.position.y = prev_y
            t_x = cos(self.direction)
            t_y = sin(self.direction)
            for i, line in enumerate(map):
                if line.distance_to(self.position) < self.size:
                    print("collision")
                    collision = True
                    # self.position.x = prev_x
                    # self.position.y = prev_y
                    # angle_intersection=self.get_angle(tan(self.direction),line.gradient())
                    # v_component=v*cos(angle_intersection)
                    # print(v,v_component)
                    # self.speed.left=v_component*self.speed.left/(self.speed.left+self.speed.right)
                    # self.speed.right = v_component * self.speed.right / (self.speed.left + self.speed.right)
                else:
                    collision = False
                if (collision == True):
                    #
                    # self.position.x = prev_x
                    # self.position.y = prev_y
                    angle_intersection = self.get_angle(tan(self.direction), line.gradient())
                    print(self.direction)
                    if (((self.direction%2*pi)>pi and (self.direction%2*pi)<2*pi) or ((self.direction%2*pi)<0 and (self.direction%2*pi) > -pi)):
                    # greater than or equal to  needed?
                        line_angle = 2*pi- atan(line.gradient())# for slide up
                    elif (((self.direction%2*pi) > 0 and (self.direction%2*pi)<pi) or ((self.direction%2*pi) < -pi and (self.direction%2*pi)>-2*pi)):
                        line_angle = pi - atan(line.gradient())  # for slide down
                    comp_angle=pi/2-angle_intersection
                    v_component = v * cos(comp_angle)
                    print(v, v_component)
                    l = v_component * self.speed.left / (self.speed.left + self.speed.right)
                    r = v_component * self.speed.right / (self.speed.left + self.speed.right)
                    R = (
                            20
                            / 2
                            * (r + l)
                            / (l - r)
                    )

                    w = (l - r) / 20

                    ICC = [
                        self.position.x - R * sin(line_angle+self.direction),
                        self.position.y + R * cos(line_angle+self.direction),
                    ]

                    a = np.array([[cos(w), -sin(w), 0], [sin(w), cos(w), 0], [0, 0, 1]])

                    b = np.array(
                        [
                            [self.position.x - ICC[0]],
                            [self.position.y - ICC[1]],
                            [line_angle+self.direction],
                        ]
                    )

                    c = np.array([[ICC[0]], [ICC[1]], [w]])

                    result = a.dot(b) + c
                    # ICC = [
                    #     self.position.x - R * sin(line_angle+self.direction),
                    #     self.position.y + R * cos(line_angle+self.direction),
                    # ]
                    # b = np.array(
                    #     [
                    #         [self.position.x - ICC[0]],
                    #         [self.position.y - ICC[1]],
                    #         [line_angle+self.direction],
                    #     ]
                    # )
                    # c = np.array([[ICC[0]], [ICC[1]], [w]])
                    #
                    # result = a.dot(b) + c
                    if round(angle_intersection,2)==round(pi/2,2) or round(angle_intersection,2)== round(3*pi/2,2):
                        self.position.x = prev_x
                        self.position.y = prev_y
                    else:
                        self.position.x = result[0][0]
                        self.position.y = result[1][0]
                        self.position.x = prev_x
                        self.position.y = prev_y
                    # self.speed.left = v_component * self.speed.left / (self.speed.left + self.speed.right)   # case for inertia considered
                    # self.speed.right = v_component * self.speed.right / (self.speed.left + self.speed.right)

                    collision = False
                    # print(v, v_component)


            # for line in map:
            #     p = Point(self.position.x,self.position.y)
            #     circle = p.buffer(self.size).boundary
            #     shapelyline= LineString([(line.start.x,line.start.y),(line.end.x,line.end.y)])
            #     intersection=circle.intersection(shapelyline)
            #     if(intersection.is_empty!=True):
            #         self.position.x = prev_x
            #         self.position.y = prev_y
            #         if(type(intersection)== shapely.geometry.linestring.LineString):
            #             point1x = intersection.xy[0][0]
            #             point1y = intersection.xy[1][0]
            #             point2x = intersection.xy[0][1]
            #             point2y = intersection.xy[1][1]
            #             midpointx=(point1x+point2x)/2
            #             midpointy=(point1y+point2y)/2
            #             sensor_disp = myFont.render(str(midpointx,midpointy), 1, (0, 0, 0))
            #             self.screen.blit(sensor_disp,self.position.to_tuple_with_movement(self.size * 3 * t_x, self.size * 3 * t_y))

            for s in self.sensors:
                s.direction = self.direction + s.offset
                s.position = self.position
