import numpy as np

def normalizeCoordinates(point):

    out = np.array([float('nan'), float('nan'), float('nan')])
    out = point;

    if not np.isnan(point[-1]) and not float(point[-1]) == 0:

        out = np.divide(point, float(point[-1]))

    return out
