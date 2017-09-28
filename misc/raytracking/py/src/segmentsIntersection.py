from src.createLine import *
from src.lineIntersection import *

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
