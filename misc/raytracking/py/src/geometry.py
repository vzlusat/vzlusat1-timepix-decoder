import numpy as np
import math

class Point:

    def __init__(self, x, y):

        self.coordinates = np.array([x, y, 1])

class Line:

    def __init__(self, point1, point2=0):

        if point2 == 0:
            self.line = point1
        else:
            self.point1 = point1
            self.point2 = point2
            self.line = np.cross(point1.coordinates, point2.coordinates)

class Segment:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.line = Line(x, y)

    def __eq__(self, other):

        if not isinstance(other, Segment):
            return 0
        
        if not np.array_equal(self.x, other.x):
            return 0

        if not np.array_equal(self.y, other.y):
            return 0

        return 1

def angleVectors(common, p1, p2):

    vec1 = normalizeLine(p1.coordinates - common.coordinates)
    vec2 = normalizeLine(p2.coordinates - common.coordinates)

    scalar = float(vec1[0])*float(vec2[0]) + float(vec1[1])*float(vec2[1])

    size1 = math.sqrt(math.pow(float(vec1[0]), 2) + math.pow(float(vec1[1]), 2))
    size2 = math.sqrt(math.pow(float(vec2[0]), 2) + math.pow(float(vec2[1]), 2))

    # try:
    angle = math.acos(scalar/(size1*size2))
    # except:
        # angle = math.acos(1.0)

    return angle

def normalizeCoordinates(point):

    out = np.array([float('nan'), float('nan'), float('nan')])
    out = point;

    if not np.isnan(point[-1]) and not float(point[-1]) == 0:

        out = np.divide(point, float(point[-1]))

    return out

def normalizeLine(line):

    out = line;

    factor = 1.0/math.sqrt(math.pow(float(line[0]), 2.0) + math.pow(float(line[1]), 2.0))

    line[0] *= factor
    line[1] *= factor
    line[2] *= factor

    return out

def linesIntersection(line1, line2):

    point = np.array([float('nan'), float('nan'), float('nan')])
    point = np.cross(line1.line, line2.line)

    coordinates = normalizeCoordinates(point)

    new_point = Point(coordinates[0], coordinates[1])

    return new_point

def segmentLineIntersection(segment, line):
    
    # calculate the intersection
    intersection = linesIntersection(segment.line, line)

    # make the segment vector
    segment_vector = segment.y.coordinates - segment.x.coordinates

    # print("segment_vector: {}".format(segment_vector))
    
    # calculate alpha
    alpha = np.array([float('nan'), float('nan'), float('nan')])
    for i in range(3):
        if not segment_vector[i] == 0:
            alpha[i] = np.divide((intersection.coordinates[i] - segment.x.coordinates[i]), segment_vector[i])

    # print("alpha: {}".format(alpha))

    alpha = [alpha[i] for i in range(len(alpha)) if not np.isnan(alpha[i])]
    alpha = [alpha[i] for i in range(len(alpha)) if not np.isinf(alpha[i])]

    # print("alpha: {}".format(alpha))
    
    if np.isnan(alpha).any():
        return float('nan')
    else:

        count = 0
        for number in alpha:
            if number >= 0 and number <= 1:
                count += 1

        if count == len(alpha):
            return intersection
        else:
            return float('nan')

def segmentsIntersection(segment1, segment2):
    
    # calculate the intersection
    intersection = linesIntersection(segment1.line, segment2.line)

    # make the segment vectors
    segment1_vector = segment1.y.coordinates - segment1.x.coordinates
    segment2_vector = segment2.y.coordinates - segment2.x.coordinates

    # print("segment_vector: {}".format(segment_vector))
    
    # calculate alpha
    alpha1 = np.array([float('nan'), float('nan'), float('nan')])
    for i in range(3):
        if not segment1_vector[i] == 0:
            alpha1[i] = np.divide((intersection.coordinates[i] - segment1.x.coordinates[i]), segment1_vector[i])

    alpha2 = np.array([float('nan'), float('nan'), float('nan')])
    for i in range(3):
        if not segment2_vector[i] == 0:
            alpha2[i] = np.divide((intersection.coordinates[i] - segment2.x.coordinates[i]), segment2_vector[i])

    # print("alpha: {}".format(alpha))

    alpha1 = [alpha1[i] for i in range(len(alpha1)) if not np.isnan(alpha1[i])]
    alpha1 = [alpha1[i] for i in range(len(alpha1)) if not np.isinf(alpha1[i])]

    alpha2 = [alpha2[i] for i in range(len(alpha2)) if not np.isnan(alpha2[i])]
    alpha2 = [alpha2[i] for i in range(len(alpha2)) if not np.isinf(alpha2[i])]

    # print("alpha1[0]: {}".format(alpha1[0]))
    # print("alpha2[0]: {}".format(alpha2[0]))

    # print("alpha: {}".format(alpha))

    int_in1 = 0
    int_in2 = 0

    if not np.isnan(alpha1).any():

        count = 0
        for number in alpha1:
            if number >= 0 and number <= 1:
                count += 1

        if count == len(alpha1):
            int_in1 = 1 

    if not np.isnan(alpha2).any():

        count = 0
        for number in alpha2:
            if number >= 0 and number <= 1:
                count += 1

        if count == len(alpha2):
            int_in2 = 1 

    if int_in1 == 1 and int_in2 == 1:
        return intersection
    else:
        return float('nan')

def reflectionTransform(line):

    out = np.array(
        [[math.pow(line.line[1], 2)-math.pow(line.line[0], 2), -2*line.line[0]*line.line[1], -2*line.line[0]*line.line[2]],
         [-2*line.line[0]*line.line[1], math.pow(line.line[0], 2)-math.pow(line.line[1], 2), -2*line.line[1]*line.line[2]],
         [0, 0, math.pow(line.line[0], 2)+math.pow(line.line[1], 2)]]
    )

    return out

def perpendicularSegment(segment, point, length=0):

    vector = segment.y.coordinates - segment.x.coordinates

    perp_vector = normalizeLine([-vector[1], vector[0], vector[2]])

    point1 = Point(point.coordinates[0]-0.5*perp_vector[0], point.coordinates[1]-0.5*perp_vector[1])
    point2 = Point(point.coordinates[0]+0.5*perp_vector[0], point.coordinates[1]+0.5*perp_vector[1])

    out = Segment(point1, point2) 

    return out

def translationTransform(a, b):

    return np.array([[1, 0, a], [0, 1, b], [0, 0, 1]])

def rotationTransform(angle):

    return np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])

def rotationAroundPointTransform(angle, point):

    a = point_min.coordinates[0]
    b = point_min.coordinates[1]

    A = translationTransform(a, b)
    A = A.dot(rotationTransform(angle))
    A = A.dot(translationTransform(-a, -b))

    return A

def reflectPointOverLine(line, point):

    # give me the reflection matrix of the line
    reflex = reflectionTransform(line)

    reflected_point = normalizeCoordinates(reflex.dot(point.coordinates))

    return Point(float(reflected_point[0]), float(reflected_point[1]))

def pointDistance(point1, point2):

    return math.sqrt(math.pow(float(point1.coordinates[0])-float(point2.coordinates[0]), 2)+math.pow(float(point1.coordinates[1])-float(point2.coordinates[1]), 2))

def deg2rad(deg):
    
    return (math.pi/180)*deg

def rad2deg(rad):
    
    return (180.0/math.pi)*rad
