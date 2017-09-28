import numpy as np

def normalizeLine(line):

    out = line;

    factor = np.sqrt(np.power(float(line[0]), 2) + np.power(float(line[1]), 2))

    out = np.divide(line, factor)

    return out
