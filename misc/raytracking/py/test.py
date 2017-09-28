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

segment_buffer = []
point_buffer = []

segments = []

point1 = Point(0, -2)
point2 = Point(10, -2)

point3 = Point(0, 1)
point4 = Point(10, 1)

# point5 = Point(13, 3)
# point6 = Point(5, -6)
# point5 = Point(-3, 3)
# point6 = Point(9, -2)
point5 = Point(6, 10)
point6 = Point(5, 0)

left1 = Point(-10, -10)
left2 = Point(-10, 10)
left = Segment(left1, left2)

segment1 = Segment(point1, point2)
segment2 = Segment(point3, point4)
segments.append(segment1)
segments.append(segment2)

plotSegment(segment_buffer, segment1, 'blue', 1)
plotSegment(segment_buffer, segment2, 'blue', 1)
plotSegment(segment_buffer, left, 'blue', 1)

plotPoint(point_buffer, point1, 'red', 30)
plotPoint(point_buffer, point2, 'red', 30)
plotPoint(point_buffer, point3, 'red', 30)
plotPoint(point_buffer, point4, 'red', 30)

ray = Segment(point5, point6)
plotSegment(segment_buffer, ray, 'green', 1)

stop = 0

for i in range(1):

    dist_min = sys.float_info.max
    point_min = 0
    inters = 0
    incident_segment = 0

    for seg in segments:

        print("pes")

        inters = segmentsIntersection(seg, ray)

        if isinstance(inters, Point):

            dist = np.sqrt(np.power(inters.coordinates[0]-ray.x.coordinates[0], 2)+np.power(inters.coordinates[1]-ray.x.coordinates[1], 2))

            if dist < dist_min:
                dist_min = dist
                point_min = inters
                incident_segment = seg

    print("dist_min: {}".format(dist_min))

    if isinstance(point_min, Point):

        print("kocka")

        plotPoint(point_buffer, point_min, 'blue', 100)

        l1 = normalizeLine(ray.line.line)
        l2 = normalizeLine(incident_segment.line.line)

        huhl = l1[0]*l2[0] + l1[1]+l2[1]
        print("huhl: {}".format(huhl))
        angle = (math.acos(huhl))
        print("angle: {}".format(angle))

        T1 = np.array([[1, 0, point_min.coordinates[0]], [0, 1, point_min.coordinates[1]], [0, 0, 1]])
        T2 = np.array([[1, 0, -point_min.coordinates[0]], [0, 1, -point_min.coordinates[1]], [0, 0, 1]])
        R1 = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])

        # reflection
        A = np.array([[np.power(float(incident_segment.line.line[1]), 2)-np.power(float(incident_segment.line.line[0]), 2), -2*float(incident_segment.line.line[0])*float(incident_segment.line.line[1]), -2*float(incident_segment.line.line[0])*float(incident_segment.line.line[2])],
                      [-2*float(incident_segment.line.line[0])*float(incident_segment.line.line[1]), np.power(float(incident_segment.line.line[0]), 2)-np.power(float(incident_segment.line.line[1]), 2), -2*float(incident_segment.line.line[1])*float(incident_segment.line.line[2])],
                      [0, 0, np.power(float(incident_segment.line.line[0]), 2)+np.power(float(incident_segment.line.line[1]), 2)]])

        # newc = normalizePoint(A.dot(np.cross(ray.line.line, incident_segment.line.line)))

        newc = normalizeCoordinates(T2.dot(ray.x.coordinates))
        newc = normalizeCoordinates(R1.dot(newc))
        newc = normalizeCoordinates(T1.dot(newc))
        newp = Point(newc[0], newc[1])
        print("newc: {}".format(newc))
        # ref_ray = Line(newc)
        # ref_point = linesIntersection(ref_ray, left.line)

        # ray = Segment(point_min, ref_point)

        plotPoint(point_buffer, newp, 'red', 100)
        # plotSegment(segment_buffer, ray, 'green', 1)

plt.figure(1)
ax = plt.subplot2grid((1, 1), (0, 0))
ax.axis('equal')
# ax.axis([-1, 13, -10, 10])

plotSegments(ax, segment_buffer)
plotPoints(ax, point_buffer)

plt.show()
