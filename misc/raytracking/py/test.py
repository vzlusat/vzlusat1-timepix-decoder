#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import time
import sys
import math

from src.geometry import *
from src.plotting import *

np.set_printoptions(precision=2)

segment_buffer = []
point_buffer = []

segments = []

point1 = Point(-5, -1.0)
point2 = Point(5, -1)

point3 = Point(-5, 0.0)
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

max_iter = 2

for i in range(max_iter):

    dist_min = sys.float_info.max
    point_min = 0
    inters = 0
    incident_segment = 0

    for seg in segments:

        if prev_segment == seg:
            continue

        inters = segmentsIntersection(seg, ray)

        if isinstance(inters, Point):

            dist = pointDistance(inters, ray.x)

            if dist < dist_min:
                dist_min = dist
                point_min = inters
                incident_segment = seg

    # print("dist_min: {}".format(dist_min))

    if isinstance(point_min, Point):

        prev_segment = incident_segment

        print("incident point: {}".format(point_min.coordinates))

        plotPoint(point_buffer, point_min, 'blue', 50)

        # create a normal segment to the incident segment in the incident point
        normal_segment = perpendicularSegment(incident_segment, point_min)
        # plotSegment(segment_buffer, normal_segment, 'red', 1)

        reflected_source = reflectPointOverLine(normal_segment.line, ray.x)

        angle = angleVectors(point_min, ray.x, reflected_source)
        print("angle: {}".format(angle, (180/np.pi)*angle))

        # stratch the new ray out
        segment_vector = reflected_source.coordinates - point_min.coordinates
        reflected_source.coordinates += 10*segment_vector

        ray_plot = Segment(ray.x, point_min)
        plotSegment(segment_buffer, ray_plot, 'green', 1)

        ray = Segment(point_min, reflected_source)

    else:
        i = max_iter


plt.figure(1)
ax = plt.subplot2grid((1, 1), (0, 0))
ax.axis('equal')
# ax.axis([-1, 13, -10, 10])

plotSegments(ax, segment_buffer)
plotPoints(ax, point_buffer)

plt.show()
