import numpy as np
from src.normalizeCoordinates import *
from src.Point import *

def linesIntersection(line1, line2):

    coordinates = normalizeCoordinates(np.cross(line1.line, line2.line))

    new_point = Point(coordinates[0], coordinates[1])

    return new_point
