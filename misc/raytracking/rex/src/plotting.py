import numpy as np
from src.geometry import *
import copy

class PointForPrint:

    def __init__(self, point, color, size):

        self.point = point
        self.color = color
        self.size = size

class SegmentForPrint:

    def __init__(self, segment, color, width):

        self.segment = segment
        self.color = color
        self.width = width

def plotPoint(point_buffer, point, color, width):

    if isinstance(point, Point):

        new_point = PointForPrint(point, color, width)

        point_buffer.append(new_point)

def plotPoints(ax, point_buffer, H=0):

    for i in range(len(point_buffer)):

        if not H == 0:

            temp_point = copy.deepcopy(point_buffer[i].point.coordinates)  

            temp_point = normalizeCoordinates(H * temp_point)

            ax.scatter(temp_point[0], temp_point[1], s=point_buffer[i].size, c=point_buffer[i].color)

        else:

            ax.scatter(point_buffer[i].point.coordinates[0], point_buffer[i].point.coordinates[1], s=point_buffer[i].size, c=point_buffer[i].color)

def plotSegment(segment_buffer, segment, color, width):

    new_segment = SegmentForPrint(segment, color, width)

    segment_buffer.append(new_segment)

def plotSegments(ax, segment_buffer, H=0):

    for i in range(len(segment_buffer)):

        temp_point1 = copy.deepcopy(segment_buffer[i].segment.x)  
        temp_point2 = copy.deepcopy(segment_buffer[i].segment.y)  

        if not isinstance(temp_point1, Point) or not isinstance(temp_point2, Point):
            continue

        if not H == 0:

            temp_point1 = normalizePoint(H * temp_point1)
            temp_point2 = normalizePoint(H * temp_point2)

        else:

            ax.plot([temp_point1.coordinates[0], temp_point2.coordinates[0]], [temp_point1.coordinates[1], temp_point2.coordinates[1]], linewidth=segment_buffer[i].width, color=segment_buffer[i].color)
