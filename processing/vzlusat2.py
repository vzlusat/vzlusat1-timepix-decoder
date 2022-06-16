#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np
import calendar

from include.baseMethods import *

tle11, tle12, tle_time1 = initializeTLE("tle.txt")
tle21, tle22, tle_time2 = initializeTLE("tle2.txt")

from_time = "16.06.2022 20:00:00"
to_time = "18.06.2022 20:00:00"

hkc_buffer_time = 300

anomaly_dt = 240

approx_north_pole = 20
approx_south_pole = 30
latitude_limit = 8

from_to = np.array([
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
[44648, 45813], # 13th full res
[45826, 46193], # 14th full res
[46246, 46659], # 15th full res
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

mesh_size = 32

step_size = 60

measurement_period = 180

max_exposure = 2.0
min_exposure = 0.004

epsilon=10.0
x_label = 'Pixel count'
x_units = '(counts)'

directory="scripts_vzlusat2"

# prepare data
images = loadImageRangeMulti(from_to, 1, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 1e-5, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images, tle11, tle12, tle_time1)

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

file_name = directory+"/{}.pln".format(from_time).replace(' ', '_').replace(':', '_')

from scipy import spatial

class ExposureUpdate:

    def __init__(self, time, action, latitude, longitude, exposure):

        self.time = time
        self.action = action
        self.latitude = latitude
        self.longitude = longitude
        self.exposure = exposure

class MeasureUpdate:

    def __init__(self, time, latitude, longitude, exposure):

        self.time = time
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
last_image_time = 0
while i <= t_end:

    latitude, longitude, tle_date = getLatLong(int(i), tle21, tle22, tle_time2)

    print("latitude: {} deg, longitude: {} deg, time: {} s".format(latitude, longitude, time))

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
    else:
        if (state == True) and not in_pole(latitude):
            state = False
            updates.append(ExposureUpdate(i, state, latitude, longitude, int(round(max_exposure*1000.0))))

    if i > last_image_time + measurement_period:

        last_image_time = i

        updates.append(MeasureUpdate(i, latitude, longitude, state))

    states.append(state)

    i += step_size

# postprocess the update list
# remove close pairs
print("Pruning update list")

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)

# new_updates_list = []

# for idx,x in enumerate(updates):

#     # the last step
#     if idx == len(updates)-1:
#         if abs(updates[idx].time - updates[idx-1].time) >= 300:
#             new_updates_list.append(updates[idx])
#     else:
#         if abs(updates[idx].time - updates[idx+1].time) >= 300:
#             new_updates_list.append(updates[idx])

# updates = new_updates_list

# duplicate setting commands

def get_time(t):
    return datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

print("Exporting planner script")
hkc_start_time = 0
with open(file_name, "w") as file:

    t = t_start

    prev_update_time = 0

    # parameter setting during the orbit
    for idx,update in enumerate(updates):

        if isinstance(update, ExposureUpdate):

          t = update.time
          
          if update.action:
              file.write(get_time(t)+" exposure {}\r\n".format(update.exposure))
          else:
              file.write(get_time(t)+" exposure {}\r\n".format(update.exposure))

        if isinstance(update, MeasureUpdate):
              file.write(get_time(t)+" measure\r\n")

        prev_update_time = t

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

    # marks the transitions
    for idx,update in enumerate(updates):

        if isinstance(update, ExposureUpdate):

            x, y = m(update.longitude, update.latitude)
            if update.exposure < 10:
                color = 'red'
            else:
                color = 'blue'
            m.scatter(x, y, 100, marker='o', color=color, zorder=5)

        if isinstance(update, MeasureUpdate):

            x, y = m(update.longitude, update.latitude)
            if update.exposure:
                color = 'red'
            else:
                color = 'blue'
            m.scatter(x, y, 100, marker='o', color=color, zorder=5)

    # mark the start
    # x, y = m(image_actions[0].longitude, image_actions[0].latitude)
    # m.scatter(x, y, 100, marker='o', color='green', zorder=5)

    # mark the end
    # x, y = m(image_actions[-1].longitude, image_actions[-1].latitude)
    # m.scatter(x, y, 100, marker='o', color='black', zorder=5)

    plt.title('VZLUSAT2 scanning, starting on {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}.png".format(from_time).replace(' ', '_').replace(':', '_'), dpi=120, bbox_inches='tight')

    # #} end of globe south

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
