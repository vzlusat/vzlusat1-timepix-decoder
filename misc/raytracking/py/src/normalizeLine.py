import numpy as np
import math

def normalizeLine(line):

    out = line;

    factor = 1.0/math.sqrt(math.pow(float(line[0]), 2.0) + math.pow(float(line[1]), 2.0))

    line[0] *= factor
    line[1] *= factor
    line[2] *= factor

    return out
