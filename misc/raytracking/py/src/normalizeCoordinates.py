import numpy as np

def normalizeCoordinates(point):

    out = point;

    if not np.isnan(point[-1]) and not point[-1] == 0:

        out = point / point[-1];

    return out
