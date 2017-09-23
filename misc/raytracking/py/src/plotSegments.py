import copy
from src.normalizeCoordinates import *
from src.Point import *

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
