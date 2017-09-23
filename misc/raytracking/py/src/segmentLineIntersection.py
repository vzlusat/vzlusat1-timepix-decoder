from src.createLine import *
from src.lineIntersection import *

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
