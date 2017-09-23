import copy
from src.normalizeCoordinates import *

def plotPoints(ax, point_buffer, H=0):

    for i in range(len(point_buffer)):

        if not H == 0:

            temp_point = copy.deepcopy(point_buffer[i].point.coordinates)  

            temp_point = normalizeCoordinates(H * temp_point)

            ax.scatter(temp_point[0], temp_point[1], s=point_buffer[i].size, c=point_buffer[i].color)

        else:

            ax.scatter(point_buffer[i].point.coordinates[0], point_buffer[i].point.coordinates[1], s=point_buffer[i].size, c=point_buffer[i].color)
