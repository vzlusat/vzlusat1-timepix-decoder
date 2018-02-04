#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time

from include.baseMethods import *

from_time = "04.02.2018 20:00:00"
to_time = "06.02.2018 20:00:00"

anomaly_lat = -30.0
anomaly_long = -40.0
anomaly_size = 45.0
desired_fill = 500
max_exposure = 1
hkc_buffer_time = 300

aprox_pole = 30
latitude_limit = 8

from_idx = 14425
to_idx = 15115
outliers=[]

pcolor_min = 0
pcolor_max = 7

epsilon=1.0
x_label = 'Pixel count'
x_units = '(counts)'

total_chunks = 0

directory="scripts_poles"

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 1, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(360)

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

#} end of RBF interpolation

t = int(time.mktime(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))
t_end = int(time.mktime(time.strptime(to_time, "%d.%m.%Y %H:%M:%S")))

file_name = directory+"/{}_anomaly.pln".format(from_time).replace(' ', '_').replace(':', '_')

from scipy import spatial

points_x = []
points_y = []

for j in range(0, 1000):
    points_x.append(0)
    points_y.append(0)

n_points = 0

def is_free(x, y):

    for j in range(0, n_points):

        if math.sqrt(math.pow(x-points_x[j], 2)+math.pow(y-points_y[j], 2)) <= 30:

            return False

    return True

with open(file_name, "w") as file:

    print("t: {}".format(t))

    lats = []
    lons = []
    times = []

    # find the closest point to the anomaly in each orbit
    i = t
    best_time = 0

    max_pxl_count = 0
    max_time = 0
    max_lat = 0
    max_lon = 0
    are_in = False

    in_first = False
    in_second = False 

    while i <= t_end:

        latitude, longitude, tle_date = getLatLong(int(i))

        if not are_in:

            fut_latitude, fut_longitude, fut_tle_date = getLatLong(i+10)

            # we are not in the equator belt
            if abs(latitude) > 40:

                # we enter from the equator belt
                if (((latitude > -45) and (fut_latitude < -45)) or ((latitude < 45) and (fut_latitude > 45))):

                    are_in = True
                    in_first = True
                    max_pxl_count = 0
                    best_time = 0
                    print("Entered the first: latitude: {}, longitude: {}".format(latitude, longitude))

                elif ((latitude > (90 - latitude_limit)) or (latitude < (-90 + latitude_limit))):

                    are_in = True
                    in_second = True
                    in_first = False
                    max_pxl_count = 0
                    best_time = 0
                    print("Entered the second: latitude: {}, longitude: {}".format(latitude, longitude))

        if are_in:

            pxl_count = doses_rbf_lin[int(math.floor(360*((longitude+180)/360))), int(math.floor(360*((latitude+90)/180)))]

            # we left the area
            # if (((latitude > 0) and (latitude > (90 - latitude_limit))) or ((latitude < 0) and (latitude < (-90 + latitude_limit)))):

            if in_first:

                # times.append(i)

                if (((latitude > 0) and (latitude > (90 - latitude_limit))) or ((latitude < 0) and (latitude < (-90 + latitude_limit)))):

                    are_in = False
                    in_first = False

                    if best_time > 1 and is_free(latitude, longitude):

                        times.append(best_time)

                        points_x[n_points] = latitude
                        points_y[n_points] = longitude

                        print("Appending: latitude: {}, longitude: {}".format(latitude, longitude))

                        n_points += 1
                    
                    max_pxl_count = 0
                    best_time = 0

                    print("Left first: latitude: {}, longitude: {}".format(latitude, longitude))

            elif in_second:

                if (abs(latitude - (90 - 2*aprox_pole)) < 1) or (abs(latitude - (-90 + 2*aprox_pole)) < 1):

                    are_in = False
                    in_second = False

                    if best_time > 1 and is_free(latitude, longitude):

                        times.append(best_time)

                        points_x[n_points] = latitude
                        points_y[n_points] = longitude

                        n_points += 1

                    max_pxl_count = 0
                    best_time = 0

                    print("Left second: latitude: {}, longitude: {}".format(latitude, longitude))

            if pxl_count >= max_pxl_count:

                if is_free(latitude, longitude):

                    max_pxl_count = pxl_count
                    best_time = i
                    print("Found max: latitude: {}, longitude: {}, value: {}".format(latitude, longitude, pxl_count))

        i += 10

# scan the surroundigs of the locations
    out_lats = []
    out_lons = []
    out_times = []
    out_pxl_counts = []
    first = 1
    last_exposure = 0
    for i in range(len(times)):

        t_now = times[i]

        if first == 1:
            first = 0
            time = datetime.datetime.utcfromtimestamp(t_now-60-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\tP\tx pwr 1\r\n")
            time = datetime.datetime.utcfromtimestamp(t_now-59-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\tP\tsleep 4000\r\n")
            time = datetime.datetime.utcfromtimestamp(t_now-55-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\tP\tx sp 404 1 70 0 1 {} 80 0 0 1\r\n".format(1+2+4+8+32))
            time = datetime.datetime.utcfromtimestamp(t_now-50-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
            file.write(time+"\tP\th conf 3 3 0 01400000000000000000\r\n")
            
        time = datetime.datetime.utcfromtimestamp(t_now-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
        file.write(time+"\tP\th go 3 1\r\n")
        
        latitude, longitude, tle_date = getLatLong(int(t_now))
        out_lats.append(latitude)
        out_lons.append(longitude)
        out_times.append(t_now)
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

        # if desired_exposure != last_exposure:
        #   time = datetime.datetime.utcfromtimestamp(t_now-20).strftime('%Y-%m-%d %H:%M:%S')
        #   file.write(time+"\t\tx se {}\r\n".format(desired_exposure))
        #   last_exposure = desired_exposure

        # time = datetime.datetime.utcfromtimestamp(t_now-15).strftime('%Y-%m-%d %H:%M:%S')
        # file.write(time+"\t\tx m\r\n")

        print("latitude: {}, longitude: {}, intensity: {}".format(latitude, longitude, pxl_count))

        # time = datetime.datetime.utcfromtimestamp(t_now+hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
        # file.write(time+"\tP\th stop 3 1\r\n")

    # time = datetime.datetime.utcfromtimestamp(out_times[-1]+300).strftime('%Y-%m-%d %H:%M:%S')
    # file.write(time+"\tP\tx pwr 0\r\n")
    # time = datetime.datetime.utcfromtimestamp(out_times[-1]+300+hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
    
fig1 = []

def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    for i in range(len(out_lats)):
        x, y = m(out_lons[i], out_lats[i])
        m.scatter(x, y, 80, marker='o', color='k', zorder=10)

    # cb.set_label('log10('+x_label+') '+x_units)
    plt.title('Anomaly scanning, starting at {}'.format(from_time))

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    plt.savefig(directory+"/{}_anomaly.jpg".format(from_time).replace(' ', '_').replace(':', '_'), dpi=60, bbox_inches='tight')

    plt.show()

print("total_chunks: {}".format(total_chunks))

file_name = directory+"/{}_anomaly.meta.txt".format(from_time).replace(' ', '_').replace(':', '_')

with open(file_name, "w") as file:

    file.write("from: "+from_time+"\r\n")
    file.write("to: "+to_time+"\r\n")
    file.write("desired fill: {} px per image\r\n".format(desired_fill))
    file.write("estimated number of chunks: {}\r\n".format(int(total_chunks)))
    file.write("based on data range: {} to {}\r\n".format(from_idx, to_idx))
    file.write("anomaly lat, long: {}, {}\r\n".format(anomaly_lat, anomaly_long))
    file.write("anomaly radius: {} deg\r\n".format(anomaly_size))
    file.write("max blunt exposure time: {} ms".format(max_exposure))

pid = os.fork()
if pid == 0:
    plot_everything()
