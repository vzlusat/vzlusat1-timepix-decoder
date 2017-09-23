import numpy as np
from src.Point import *

def plotPoint(point_buffer, point, color, width):

    if isinstance(point, Point):

        new_point = PointForPrint(point, color, width)

        point_buffer.append(new_point)
