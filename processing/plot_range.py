#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np
import calendar

from include.baseMethods import *

tle1, tle2, tle_time = initializeTLE("tle.txt")

from_time = "10.11.2022 20:30:00"
to_time = "12.11.2022 20:00:00"

hkc_buffer_time = 300

anomaly_dt = 240

approx_north_pole = 20
approx_south_pole = 30
latitude_limit = 8

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
# [44648, 45813], # 13th full res
# [45826, 46193], # 14th full res
# [46246, 46659], # 15th full res
[51785, 52939], # 22th full res
])

outliers=[]

anomaly_lat = -37.0
anomaly_long = -31.0
anomaly_size = 45.0

sgap_lat = -80.0
sgap_long = 125.0
sgap_size = 25.0

pcolor_min = 0
pcolor_max = 6

mesh_size = 100

step_size = 10

max_exposure = 2.0
min_exposure = 0.004

epsilon=10.0
x_label = 'Pixel count'
x_units = '(counts)'

directory="scripts_hybrid"

# prepare data
images = loadImageRangeMulti(from_to, 1, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images, tle1, tle2, tle_time)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

# # #{ RBF interpolation

# create meshgrid for RBF
print("Interpolating")

x_meshgrid, y_meshgrid = createMeshGrid(mesh_size)

# calculate RBF from log data
rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=epsilon, smooth=1)
doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=epsilon, smooth=1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

# plt.figure(2)
# ax1 = plt.subplot2grid((1, 1), (0, 0))
# plt.imshow(doses_rbf_lin)
# plt.show()

# # #} end of RBF interpolation

def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1)

    # #{ map

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Log of relative intensity [px flux]") # draw colorbar

    plt.title('Hybrid scanning, starting on {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}_hybrid.png".format(from_time).replace(' ', '_').replace(':', '_'), dpi=120, bbox_inches='tight')

    # #} end of globe south

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
