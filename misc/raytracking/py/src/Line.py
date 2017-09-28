import numpy as np

class Line:

    def __init__(self, point1, point2=0):

        if point2 == 0:
            self.line = point1
        else:
            self.point1 = point1
            self.point2 = point2
            self.line = np.cross(point1.coordinates, point2.coordinates)

