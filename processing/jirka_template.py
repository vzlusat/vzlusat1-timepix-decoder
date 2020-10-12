#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_to = numpy.array([
# [36352, 36671], # 1st full res
# [36672, 37034], # 2nd full res
# [37103, 37862], # 3rd full res
# [37863, 38587], # 4th full res
# [38604, 39191], # 5th full res
# [39194, 39961], # 6th full res
# [39962, 40568], # 7th full res
# [40600, 41429], # 8th full res
# [41446, 42354], # 9th full res
# [42355, 43038], # 10th full res
# [43072, 43963], # 11th full res
# [43964, 44569], # 12th full res
[44648, 45813], # 13th full res
# [45826, 46193], # 14th full res
])
outliers=[]

# load images from database
images = loadImageRangeMulti(from_to, 1, 1, 1, outliers)

# calculate radiation dose from images
doses = calculateEnergyDose(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

# obtain GPS coordinates
lats_orig, lons_orig = extractPositions(images)

print("doses: {}".format(doses))
print("lats_orig: {}".format(lats_orig))
print("lons_orig: {}".format(lons_orig))
