#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np

from include.baseMethods import *

from_time = "12.07.2019 10:00:00"
to_time = "13.07.2019 10:00:00"

desired_fill = 50
ax_exposure = 0.03
hkc_buffer_time = 300

n = 1

anomaly_dt = 240

approx_north_pole = 20
approx_south_pole = 30
latitude_limit = 8

from_to = numpy.array([
[22617, 23690], # dos 31
[23693, 24730], # dos 32
[24738, 25754], # dos 33
[26671, 27784], # dos 34
])

outliers=[]

anomaly_lat = -37.0
anomaly_long = -31.0
anomaly_size = 45.0

sgap_lat = -80.0
sgap_long = 125.0
sgap_size = 25.0

pcolor_min = 0
pcolor_max = 7

mesh_size = 100

step_size = 60.0

max_exposure = 0.1

epsilon=10.0
x_label = 'Pixel count'
x_units = '(counts)'

total_chunks = 0

directory="scripts_hybrid"

# prepare data
images = loadImageRangeMulti(from_to, 32, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

# # #{ RBF interpolation

# create meshgrid for RBF
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

t = int(time.mktime(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))
t_end = int(time.mktime(time.strptime(to_time, "%d.%m.%Y %H:%M:%S")))

file_name = directory+"/{}_combined.pln".format(from_time).replace(' ', '_').replace(':', '_')

from scipy import spatial

lats = []
lons = []
times = []
# orbits = []
orbit_line_lats = []
orbit_line_lons = []
pxl_counts = []
states = []

def is_free(x, y):

    num = 0

    for j in range(0, len(lats)):

        if dist(x, y, lats[j], lons[j]) < 8:

            return False

    return True

def in_anomaly(latitude, longitude):

    # if the anomaly is close
    anomaly_dist = dist(latitude, longitude, anomaly_lat, anomaly_long)
    if (anomaly_dist < anomaly_size) and (latitude > -70):

        return True

    else:

        return False

def in_pole(latitude):

    # we are not in the equator belt
    if ((latitude > 0) and (abs(latitude) > (90 - (2*approx_north_pole + 1)))) or ((latitude < 0) and (abs(latitude) > (90 - (2*approx_south_pole + 1)))):
        return True
    else:
        return False

# scan for the anomaly
i = t
while i <= t_end:

    latitude, longitude, tle_date = getLatLong(int(i))

    lats.append(latitude)
    lons.append(longitude)
    times.append(i)

    pxl_count = doses_rbf_log[int(math.floor(mesh_size*((longitude+180)/360))), int(math.floor(mesh_size*((latitude+90)/180)))]

    pxl_counts.append(pxl_count)

    # if pxl_count > 100:
    #     state = True
    # else:
    #     state = False

    if in_pole(latitude) or in_anomaly(latitude, longitude):
        state = True
    else:
        state = False

    states.append(state)

    i += step_size

def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=2)

    # #{ map

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Log of relative intensity [px flux]") # draw colorbar

    for i in range(len(lats)):
        x, y = m(lons[i], lats[i])
        if states[i]:
            color = 'red'
        else:
            color = 'blue'
        m.scatter(x, y, 20, marker='o', color=color, zorder=5)

        # plt.text(x+1, y+1, '{}'.format(out_orbits[i]), fontsize=13, fontweight='bold', ha='left', va='bottom', color='k', zorder=10)

    # cb.set_label('log10('+x_label+') '+x_units)
    plt.title('Combined scanning, starting on {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}_combined.png".format(from_time).replace(' ', '_').replace(':', '_'), dpi=60, bbox_inches='tight')

    # #} end of globe south

    ax1 = plt.subplot2grid((1, 2), (0, 1), colspan=1, rowspan=2)

    # #{ pxlcount

    plt.plot(times, pxl_counts)

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    # #} end of globe south

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
