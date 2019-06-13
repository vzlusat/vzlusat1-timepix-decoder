#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_to = numpy.array([[1, 40000]])

outliers=[]

# prepare data
images = loadImageRangeMulti(from_to, 1, 0, 1, outliers)

total_exposure_time = calculateTotalExposureTime(images)
print("total_exposure_time: {} s ... ({} hours)".format(total_exposure_time, total_exposure_time/3600.0))

print("total_processing_time: {} s ... ({} hours)".format(total_exposure_time + len(images)*12, (total_exposure_time + len(images)*12)/3600.0))
