#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import pickle
import time
import sys
import math

from src.lineIntersection import *
from src.Segment import Segment
from src.Point import Point
from src.Line import Line
from src.segmentLineIntersection import *
from src.segmentsIntersection import *
from src.plotPoint import *
from src.plotPoints import *
from src.plotSegment import *
from src.plotSegments import *
from src.normalizeCoordinates import *
from src.normalizeLine import *
from src.angleVectors import *

np.set_printoptions(precision=2)

segment_buffer = []
point_buffer = []

segments = []

point1 = Point(-5, -1.1)
point2 = Point(5, -1)

point3 = Point(-5, 0.1)
point4 = Point(5, 0)

point5 = Point(8, 1)
# point5 = Point(6, 2)
point6 = Point(3.0, -1.2)

left1 = Point(-10, -10)
left2 = Point(-10, 10)
right1 = Point(10, -10)
right2 = Point(10, 10)
left = Segment(left1, left2)
bottom = Segment(left1, right1)
right = Segment(right1, right2)
top = Segment(right2, left2)

segment1 = Segment(point1, point2)
segment2 = Segment(point3, point4)
segments.append(segment1)
segments.append(segment2)
segments.append(left)
segments.append(bottom)
segments.append(top)
segments.append(right)

plotSegment(segment_buffer, segment1, 'blue', 1)
plotSegment(segment_buffer, segment2, 'blue', 1)
plotSegment(segment_buffer, left, 'blue', 1)
plotSegment(segment_buffer, top, 'blue', 1)
plotSegment(segment_buffer, bottom, 'blue', 1)
plotSegment(segment_buffer, right, 'blue', 1)

plotPoint(point_buffer, point1, 'red', 30)
plotPoint(point_buffer, point2, 'red', 30)
plotPoint(point_buffer, point3, 'red', 30)
plotPoint(point_buffer, point4, 'red', 30)

ray = Segment(point5, point6)
# plotSegment(segment_buffer, ray, 'green', 1)

stop = 0
prev_segment = 0

max_iter = 5

for i in range(max_iter):

    dist_min = sys.float_info.max
    point_min = 0
    inters = 0
    incident_segment = 0

    for seg in segments:

        if prev_segment == seg:
            print("myslivec")
            continue

        print("pes")

        inters = segmentsIntersection(seg, ray)

        if isinstance(inters, Point):

            dist = np.sqrt(np.power(float(inters.coordinates[0])-float(ray.x.coordinates[0]), 2)+np.power(float(inters.coordinates[1])-float(ray.x.coordinates[1]), 2))

            if dist < dist_min:
                dist_min = dist
                point_min = inters
                incident_segment = seg

    # print("dist_min: {}".format(dist_min))

    if isinstance(point_min, Point):

        prev_segment = incident_segment

        print("incident point: {}".format(point_min.coordinates))

        plotPoint(point_buffer, point_min, 'blue', 50)

        # l1 = normalizeLine(ray.line.line)
        # l2 = normalizeLine(incident_segment.line.line)
        # l1 = normalizeCoordinates(l1)
        # l2 = normalizeCoordinates(l2)
        # huhl = float(l1[0])*float(l2[0]) + float(l1[1])+float(l2[1])
        # print("huhl: {}".format(huhl))
        # if huhl <= 1 and huhl >= -1:
        #   if huhl >= 0:
        #       angle = (math.acos(1-huhl))
        #   else:
        #       angle = (math.acos(huhl))
        #   print("angle: {}".format(angle))
        #   angle = (np.pi - 2*angle)
        #   print("angle: {}".format(angle))

        right_angle = np.pi/2
        T1 = np.array([[1, 0, point_min.coordinates[0]], [0, 1, point_min.coordinates[1]], [0, 0, 1]])
        T2 = np.array([[1, 0, -point_min.coordinates[0]], [0, 1, -point_min.coordinates[1]], [0, 0, 1]])
        R1 = np.array([[np.cos(right_angle), -np.sin(right_angle), 0], [np.sin(right_angle), np.cos(right_angle), 0], [0, 0, 1]])

        # T1 = np.array([[1, 0, point_min.coordinates[0]], [0, 1, point_min.coordinates[1]], [0, 0, 1]])
        # T2 = np.array([[1, 0, -point_min.coordinates[0]], [0, 1, -point_min.coordinates[1]], [0, 0, 1]])
        # R1 = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])

        # newc = normalizePoint(A.dot(np.cross(ray.line.line, incident_segment.line.line)))

        newc = normalizeCoordinates(T2.dot(incident_segment.x.coordinates))
        newc = normalizeCoordinates(R1.dot(newc))
        newc = normalizeCoordinates(T1.dot(newc))
        newp = Point(float(newc[0]), float(newc[1]))

        angle = angleVectors(point_min, ray.x, newp)
        print("angle: {} {}".format(angle, (180/np.pi)*angle))

        # show reflected line
        temp_segment = Segment(newp, point_min)
        # plotSegment(segment_buffer, temp_segment, 'blue', 1)

        # reflection
        A = np.array([[np.power(float(temp_segment.line.line[1]), 2)-np.power(float(temp_segment.line.line[0]), 2), -2*float(temp_segment.line.line[0])*float(temp_segment.line.line[1]), -2*float(temp_segment.line.line[0])*float(temp_segment.line.line[2])],
                      [-2*float(temp_segment.line.line[0])*float(temp_segment.line.line[1]), np.power(float(temp_segment.line.line[0]), 2)-np.power(float(temp_segment.line.line[1]), 2), -2*float(temp_segment.line.line[1])*float(temp_segment.line.line[2])],
                      [0, 0, np.power(float(temp_segment.line.line[0]), 2)+np.power(float(temp_segment.line.line[1]), 2)]])

        # reflect the previous point
        newc = normalizeCoordinates(A.dot(ray.x.coordinates))

        # show reflected point
        newp = Point(float(newc[0]), float(newc[1]))
        # plotPoint(point_buffer, newp, 'blue', 50)

        segment_vector = newc - normalizeCoordinates(point_min.coordinates)
        newc = 10*segment_vector

        newp = Point(float(newc[0]), float(newc[1]))

        # print("newc: {}".format(newc))

        # ref_ray = Line(point_min, newp)
        # ref_point = linesIntersection(ref_ray, incident_segment.line)

        # plotPoint(point_buffer, newp, 'red', 100)
        # plotPoint(point_buffer, ref_point, 'green', 100)

        ray_plot = Segment(ray.x, point_min)
        plotSegment(segment_buffer, ray_plot, 'green', 1)

        ray = Segment(point_min, newp)

    else:
        i = max_iter


plt.figure(1)
ax = plt.subplot2grid((1, 1), (0, 0))
ax.axis('equal')
# ax.axis([-1, 13, -10, 10])

plotSegments(ax, segment_buffer)
plotPoints(ax, point_buffer)

plt.show()
