import numpy as np

class Point:

    def __init__(self, x, y):

        self.coordinates = np.array([x, y, 1])

class PointForPrint:

    def __init__(self, point, color, size):

        self.point = point
        self.color = color
        self.size = size
