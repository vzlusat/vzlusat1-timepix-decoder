#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time

from include.baseMethods import *

from_time = "06.10.2017 08:00:00"
to_time = "07.10.2017 08:00:00"

anomaly_lat = -33.0
anomaly_long = -43.0
anomaly_size = 40.0
desired_fill = 100
max_exposure = 1000

dt = 180
n = 1

from_idx = 2478
to_idx = 3332
outliers=[]

pcolor_min = 0
pcolor_max = 7

epsilon=1.0
x_label = 'Pixel count'
x_units = '(counts)'

total_chunks = 0

directory="scripts_anomaly"

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

# plt.figure(2)
# ax1 = plt.subplot2grid((1, 1), (0, 0))
# plt.imshow(doses_rbf_lin)
# plt.show()

#} end of RBF interpolation

t = int(time.mktime(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))
t_end = int(time.mktime(time.strptime(to_time, "%d.%m.%Y %H:%M:%S")))

file_name = directory+"/{}_anomaly.pln".format(from_time).replace(' ', '_')

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
    while i <= t_end:

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
            pxl_count = doses_rbf_lin[int(math.floor(100*(latitude+90)/180)), int(math.floor(100*(longitude+180)/360))]
            if pxl_count < 0:
                pxl_count = 0
            out_pxl_counts.append(pxl_count)

            if pxl_count < desired_fill:
                desired_exposure = max_exposure
            else:
                desired_exposure = int(round(1000.0/(pxl_count/desired_fill)))

                if desired_exposure == 0:
                    desired_exposure = 1

            total_chunks += 1+4+16+1+(round(((desired_exposure/1000.0)*pxl_count)/20))+1

            time = datetime.datetime.utcfromtimestamp(j-20).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\t\tx se {}\r\n".format(desired_exposure))
            time = datetime.datetime.utcfromtimestamp(j-15).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\t\tx m\r\n")

            print("latitude: {}, longitude: {}, intensity: {}".format(latitude, longitude, pxl_count))

    time = datetime.datetime.utcfromtimestamp(out_times[-1]+300).strftime('%Y-%m-%d %H:%M:%S')
    file.write(time+"\tP\tx pwr 0\r\n")
    
fig1 = []

def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0))

    m = createMap('ortho', anomaly_lat, anomaly_long)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    for i in range(len(out_lats)):
        x, y = m(out_lons[i], out_lats[i])
        m.scatter(x, y, 80, marker='o', color='k', zorder=10)

    # cb.set_label('log10('+x_label+') '+x_units)
    plt.title('Anomaly scanning, starting at {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}_anomaly.jpg".format(from_time).replace(' ', '_'), dpi=60, bbox_inches='tight')

    plt.show()

print("total_chunks: {}".format(total_chunks))

file_name = directory+"/{}_anomaly.meta.txt".format(from_time).replace(' ', '_')

with open(file_name, "w") as file:

    file.write("from: "+from_time+"\r\n")
    file.write("to: "+to_time+"\r\n")
    file.write("desired fill: {} px per image\r\n".format(desired_fill))
    file.write("estimated number of chunks: {}\r\n".format(int(total_chunks)))
    file.write("based on data range: {} to {}\r\n".format(from_idx, to_idx))
    file.write("anomaly lat, long: {}, {}\r\n".format(anomaly_lat, anomaly_long))
    file.write("anomaly radius: {} deg\r\n".format(anomaly_size))
    file.write("measurement spacing: {} seconds\r\n".format(dt))
    file.write("no. of measurements per orbit: {}\r\n".format(2*n+1))
    file.write("max exposure time: {} ms".format(max_exposure))

pid = os.fork()
if pid == 0:
    plot_everything()
