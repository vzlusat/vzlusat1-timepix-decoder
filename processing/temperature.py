#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_idx = 385
to_idx = 27000
outliers=[]

pcolor_min = 0
pcolor_max = 8

small_plot = 1

date_range = '06-07.05.2018'
x_units = '(keV/s, log)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = '31th dosimetry 500 km LEO, VZLUSAT-1'
epsilon=0.1

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 0, 1, outliers)

temperatures=[]
for i, image in enumerate(images):
    temperatures.append(image.temperature)

average = np.mean(temperatures)

print("average: {}".format(average))
