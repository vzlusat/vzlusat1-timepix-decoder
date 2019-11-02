#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np
import calendar

from include.baseMethods import *

from_time = "26.09.2019 21:55:00"
to_time = "27.09.2019 09:50:00"

hkc_buffer_time = 300

anomaly_dt = 240

approx_north_pole = 20
approx_south_pole = 30
latitude_limit = 8

from_to = numpy.array([
[32478, 35838], # filtered fullres
[36352, 36671], # 1st full res
[36672, 37034], # 2nd full res
])

outliers=[]

anomaly_lat = -37.0
anomaly_long = -31.0
anomaly_size = 45.0

sgap_lat = -80.0
sgap_long = 125.0
sgap_size = 25.0

pcolor_min = 0
pcolor_max = 4

mesh_size = 100

step_size = 30.0

max_exposure = 1.0
min_exposure = 0.002

epsilon=10.0
x_label = 'Pixel count'
x_units = '(counts)'

directory="scripts_hybrid"

# prepare data
images = loadImageRangeMulti(from_to, 1, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

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

t_start = int(calendar.timegm(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))
t_end = int(calendar.timegm(time.strptime(to_time, "%d.%m.%Y %H:%M:%S")))

file_name = directory+"/{}_hybrid.pln".format(from_time).replace(' ', '_').replace(':', '_')

from scipy import spatial

class ExposureUpdate:

    def __init__(self, time, action, latitude, longitude, exposure):

        self.time = time
        self.action = action
        self.latitude = latitude
        self.longitude = longitude
        self.exposure = exposure

lats = []
lons = []
times = []
pxl_counts = []
states = []
updates = []

# #{ is_free()

def is_free(x, y):

    num = 0

    for j in range(0, len(lats)):

        if dist(x, y, lats[j], lons[j]) < 8:

            return False

    return True

# #} end of is_free()

# #{ in_anomaly()

def in_anomaly(latitude, longitude):

    # if the anomaly is close
    anomaly_dist = dist(latitude, longitude, anomaly_lat, anomaly_long)
    if (anomaly_dist < anomaly_size) and (latitude > -70):

        return True

    else:

        return False

# #} end of in_anomaly()

# #{ in_pole()

def in_pole(latitude):

    # we are not in the equator belt
    if ((latitude > 0) and (abs(latitude) > (90 - (2*approx_north_pole + 1)))) or ((latitude < 0) and (abs(latitude) > (90 - (2*approx_south_pole + 1)))):
        return True
    else:
        return False

# #} end of in_pole()

print("Calculating orbit")
i = t_start
state = True
last_change = 0
while i <= t_end:

    latitude, longitude, tle_date = getLatLong(int(i))

    lats.append(latitude)
    lons.append(longitude)
    times.append(i)

    if i < t_start + 120:
        i += step_size
        continue

    pxl_count = doses_rbf_log[int(math.floor(mesh_size*((longitude+180)/360))), int(math.floor(mesh_size*((latitude+90)/180)))]

    pxl_counts.append(pxl_count)

    # we_are_in = in_pole(latitude) or in_anomaly(latitude, longitude) # position-based
    we_are_in = pxl_count > 1 # data-based

    if we_are_in:
        if (state == False):
            state = True
            updates.append(ExposureUpdate(i, state, latitude, longitude, int(round(min_exposure*1000.0))))
            last_change = i
    else:
        if (state == True) and not in_pole(latitude):
            state = False
            updates.append(ExposureUpdate(i, state, latitude, longitude, int(round(max_exposure*1000.0))))
            last_change = i

    states.append(state)

    i += step_size

# postprocess the update list
# remove close pairs
print("Pruning update list")
from itertools import izip

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)

new_updates_list = []

for idx,x in enumerate(updates):

    # the last step
    if idx == len(updates)-1:
        if abs(updates[idx].time - updates[idx-1].time) >= 300:
            new_updates_list.append(updates[idx])
    else:  
        if abs(updates[idx].time - updates[idx+1].time) >= 300:
            new_updates_list.append(updates[idx])

updates = new_updates_list

# duplicate setting commands

def get_time(t):
    return datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

print("Exporting planner script")
hkc_start_time = 0
hkc_period = 180
with open(file_name, "w") as file:

    t = t_start

    # power it up
    file.write(get_time(t)+"\tP\tx pwr 1\r\n")

    # wait
    t = t + 1
    file.write(get_time(t)+"\tP\tsleep 4000\r\n")

    # set overall parameters
    t = t + 4
    threshold = 385
    exposure = int(round(min_exposure*1000.0))
    bias = 70
    filtering = 0
    mode = 1
    output = 1
    temperature = 80
    pxl = 0
    uv_thr = 0
    file.write(get_time(t)+"\tP\tx sp {} {} {} {} {} {} {} {} {}\r\n".format(threshold, exposure, bias, filtering, mode, output, temperature, pxl, uv_thr))

    # setup HKC for dosimetry
    t = t + 2
    hkc_start_time = t
    file.write(get_time(t)+"\tP\th conf 1 {} 0 00000000008004000000\r\n".format(hkc_period))

    # wait
    t = t + 2
    file.write(get_time(t)+"\tP\tsleep 3000\r\n")

    # start HKC
    t = t + 3
    file.write(get_time(t)+"\tP\th go 1 1\r\n")
    
    prev_update_time = 0

    # parameter setting during the orbit
    for idx,update in enumerate(updates):

        t = update.time

        if abs(t - prev_update_time) < 300:
            print("Close points detected!!! {} {}".format(prev_update_time, t))

        if update.action:
            file.write(get_time(t-90)+"\t\tx se {}\r\n".format(update.exposure))
            file.write(get_time(t)+"\t\tx se {}\r\n".format(update.exposure))
        else:
            file.write(get_time(t-90)+"\t\tx se {}\r\n".format(update.exposure))
            file.write(get_time(t)+"\t\tx se {}\r\n".format(update.exposure))

        prev_update_time = t

    # stop HKC
    t = t + 10
    file.write(get_time(t)+"\tP\th stop 1 1\r\n")

    # power OFF
    t = t + 10
    file.write(get_time(t)+"\tP\tx pwr 0\r\n")

# simulate the orbit
class ImageAction:

    def __init__(self, time, exposure, mode, pixels, latitude, longitude):

        self.time = time
        self.exposure = exposure
        self.mode = mode
        self.pixels = pixels
        self.latitude = latitude
        self.longitude = longitude

image_actions = []

print("Prediction image actions")
state = True
i = hkc_start_time
update_idx = 0
exposure_time = 1
mode = 1
while i <= t_end:

    if update_idx < len(updates) and updates[update_idx].time < i:
        exposure_time = updates[update_idx].exposure
        mode = updates[update_idx].action
        update_idx = update_idx + 1

    latitude, longitude, tle_date = getLatLong(int(i))

    pxl_count = doses_rbf_lin[int(math.floor(mesh_size*((longitude+180)/360))), int(math.floor(mesh_size*((latitude+90)/180)))]

    image_actions.append(ImageAction(i, exposure_time, mode, pxl_count * (float(exposure_time) / 1000.0), latitude, longitude))

    i = i + hkc_period

print("Calculating statistics")
total_chunks = 0
total_memory = 0
total_pixel_count = 0

for idx,image in enumerate(image_actions):

    total_pixel_count += image.pixels
    total_chunks += (1+(int(round((image.pixels)/20.0))))

total_memory = (total_chunks*64)/1024.0

print("total_pixel_count: {}".format(total_pixel_count))
print("total_chunks: {}".format(total_chunks))
print("total_memory: {} kB".format(total_memory))

file_name = directory+"/{}_hybrid.meta.txt".format(from_time).replace(' ', '_').replace(':', '_')
with open(file_name, "w") as file:

    file.write("Planned within times:\r\n")
    file.write("  from: "+from_time+"\r\n")
    file.write("  to: "+to_time+"\r\n")
    file.write("Number of images: {}\r\n".format(len(image_actions)))
    file.write("Estimated number of chunks: {}\r\n".format(int(total_chunks)))
    file.write("Estimated memory consumption: {} kB\r\n".format(total_memory))
    file.write("Based on data range: {}\r\n".format(from_to))
    file.write("Long exposure time: {} s\r\n".format(max_exposure))
    file.write("Short exposure time: {} s\r\n".format(min_exposure))
    file.write("HKC period: {} s\r\n".format(hkc_period))

print("Plotting")
def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1)

    # #{ map

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Log of relative intensity [px flux]") # draw colorbar

    # mark the orbit
    for i in range(len(lats)):
        x, y = m(lons[i], lats[i])
        color = 'grey'
        m.scatter(x, y, 1, marker='o', color=color, zorder=5)

    # mark the measurements
    for idx,image in enumerate(image_actions):
        x, y = m(image.longitude, image.latitude)
        if image.exposure < 10:
            color = 'red'
        else:
            color = 'blue'
        m.scatter(x, y, 40, marker='x', color=color, zorder=5)

    # marks the transitions
    for idx,update in enumerate(updates):
        x, y = m(update.longitude, update.latitude)
        if update.exposure < 10:
            color = 'red'
        else:
            color = 'blue'
        m.scatter(x, y, 100, marker='o', color=color, zorder=5)

    # mark the start
    x, y = m(image_actions[0].longitude, image_actions[0].latitude)
    m.scatter(x, y, 100, marker='o', color='green', zorder=5)

    # mark the end
    x, y = m(image_actions[-1].longitude, image_actions[-1].latitude)
    m.scatter(x, y, 100, marker='o', color='black', zorder=5)

    plt.title('Hybrid scanning, starting on {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}_hybrid.png".format(from_time).replace(' ', '_').replace(':', '_'), dpi=120, bbox_inches='tight')

    # #} end of globe south

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
