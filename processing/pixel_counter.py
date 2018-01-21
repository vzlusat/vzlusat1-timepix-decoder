#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_idx = 1
to_idx = 15000
outliers=[]

pcolor_min = 0
pcolor_max = 8

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 1, 1, outliers)

# doses = calculateEnergyDose(images)
doses, total_exposure_time, total_pixel_count = calculateTotalPixelCount2(images)

print("total_exposure_time/60.0: {} min".format(total_exposure_time/60.0))
print("float(total_pixel_count)/float(total_exposure_time): {}".format(float(total_pixel_count)/float(total_exposure_time)))
