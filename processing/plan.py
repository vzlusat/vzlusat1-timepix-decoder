#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time

from include.baseMethods import *

anomaly_lat = -31.0
anomaly_long = -43.0
anomaly_size = 40.0
desired_fill = 600

from_idx = 417
to_idx = 796
outliers=[]

pcolor_min = 0
pcolor_max = 7

epsilon=1.0
x_label = 'Pixel count'
x_units = '(counts)'

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=epsilon, smooth=0.1)
doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=epsilon, smooth=0.1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

#} end of RBF interpolation

from_time = "01.10.2017 21:00:00"

t = int(time.mktime(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))

file_name = "anomaly_planner.pln"

with open(file_name, "w") as file:

    print("t: {}".format(t))

    lats = []
    lons = []
    times = []

    # find the closest point to the anomaly in each orbit
    i = t
    anomaly_close=0
    min_dist = 180.0
    best_time = 0
    while i <= t+86400:

        latitude, longitude, tle_date = getLatLong(int(i))

        # if the anomaly is close
        anomaly_dist = dist(latitude, longitude, anomaly_lat, anomaly_long)
        if anomaly_dist < anomaly_size:

            anomaly_close = 1

            # if we are closer than we were
            if anomaly_dist < min_dist:

                min_dist = anomaly_dist
                best_time = i

            i += 1

        else:

            # we just left the vicinity of the anomaly
            if anomaly_close == 1:
                latitude, longitude, tle_date = getLatLong(int(best_time))
                lats.append(latitude)
                lons.append(longitude)
                times.append(best_time)
                anomaly_close = 0
                min_dist = 180.0
                best_time = 0

            i += 60

# scan the surroundigs of the locations
    dt = 240
    n = 1
    out_lats = []
    out_lons = []
    out_times = []
    out_pxl_counts = []
    first = 1
    for i in range(len(lats)):
        
        for j in range(times[i]-n*dt, times[i]+(n+1)*dt, dt):

            if first == 1:
                first = 0
                time = datetime.datetime.utcfromtimestamp(j-60).strftime('%Y-%m-%d %H:%M:%S')
                file.write(time+"\tP\tx pwr 1\r\n")
                time = datetime.datetime.utcfromtimestamp(j-59).strftime('%Y-%m-%d %H:%M:%S')
                file.write(time+"\tP\tsleep 4000\r\n")
                time = datetime.datetime.utcfromtimestamp(j-55).strftime('%Y-%m-%d %H:%M:%S')
                file.write(time+"\tP\tx sp 405 1 70 0 1 {} 80 0 0 1\r\n".format(1+2+4+8+32))
            
            latitude, longitude, tle_date = getLatLong(int(j))
            out_lats.append(latitude)
            out_lons.append(longitude)
            out_times.append(j)
            pxl_count = doses_rbf_lin[math.floor(100*(latitude+90)/180), math.floor(100*(longitude+180)/360)]
            if pxl_count < 0:
                pxl_count = 0
            out_pxl_counts.append(pxl_count)

            if pxl_count < desired_fill:
                desired_exposure = 1000
            else:
                desired_exposure = int(round(1000.0/(pxl_count/desired_fill)))

                if desired_exposure == 0:
                    desired_exposure = 1

            time = datetime.datetime.utcfromtimestamp(j-20).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\t\t\tx se {}\r\n".format(desired_exposure))
            time = datetime.datetime.utcfromtimestamp(j-15).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\t\t\tx m\r\n")

            print("latitude: {}, longitude: {}, intensity: {}".format(latitude, longitude, pxl_count))

    time = datetime.datetime.utcfromtimestamp(out_times[-1]+300).strftime('%Y-%m-%d %H:%M:%S')
    file.write(time+"\t\t\tx pwr 0\r\n")

    def plot_everything(*args):

        # plt.figure(2)
        # ax1 = plt.subplot2grid((1, 1), (0, 0))
        # plt.imshow(doses_rbf_log)

        plt.figure(1)

        ax1 = plt.subplot2grid((1, 1), (0, 0))

        m = createMap('ortho', anomaly_lat, anomaly_long)

        x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

        m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

        cb = m.colorbar(location="bottom", label="Z") # draw colorbar

        for i in range(len(out_lats)):
            x, y = m(out_lons[i], out_lats[i])
            m.scatter(x, y, 80, marker='o', color='k', zorder=10)

        # cb.set_label('log10('+x_label+') '+x_units)
        # plt.title('RBF multiquadric (eps={}), log scale, '.format(epsilon)+date_range, fontsize=13)

        plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

        plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
