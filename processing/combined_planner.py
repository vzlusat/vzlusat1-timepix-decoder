#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np

from include.baseMethods import *

from_time = "14.03.2018 20:00:00"
to_time = "15.03.2018 20:00:00"

desired_fill = 100
max_exposure = 0.05
hkc_buffer_time = 300

n = 1

dt = 240

approx_pole = 25
latitude_limit = 8

from_to = numpy.array([
[17271, 18061], # dos 25
[18075, 18448], # dos 26
[18464, 19408], # dos 27
[18064, 18074], # poles 1
[18452, 18463], # poles 2
[19412, 19432], # poles 3
[7736, 7777], # anomaly 6
[8839, 8893], # anomaly 7
])

outliers=[]

anomaly_lat = -37.0
anomaly_long = -31.0
anomaly_size = 35.0

sgap_lat = -80.0
sgap_long = 125.0
sgap_size = 25.0

pcolor_min = 0
pcolor_max = 7

mesh_size = 200

step_size = 15

epsilon=0.1
x_label = 'Pixel count'
x_units = '(counts)'

total_chunks = 0

directory="scripts_combined"

# prepare data
images = loadImageRangeMulti(from_to, 32, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

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

#} end of RBF interpolation

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

def is_free(x, y):

    num = 0

    for j in range(0, len(lats)):

        if dist(x, y, lats[j], lons[j]) < 10:

            return False

        # if x < 0 and lats[j] < 0:
        #     if abs(y - lons[j]) < 18:

        #         return False

        # if x > 0 and lats[j] > 0:
        #     if abs(y - lons[j]) < 18:

        #         return False

    return True

def add(x, y, best_time, orbit_n):

    if is_free(x, y):

        times.append(best_time)
        lats.append(x)
        lons.append(y)
        # orbits.append(orbit_n)

        return True

    else:

        return False

with open(file_name, "w") as file:

    print("t: {}".format(t))

    # scann for the anomaly
    i = t
    anomaly_close=0
    min_dist = 180.0
    best_time = 0
    while i <= t_end:

        latitude, longitude, tle_date = getLatLong(int(i))

        # if the anomaly is close
        anomaly_dist = dist(latitude, longitude, anomaly_lat, anomaly_long)
        if (anomaly_dist < anomaly_size) and (latitude > -70):

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

    # generate anomaly sampling
    anom_lats = []
    anom_lons = []
    anom_times = []
    out_pxl_counts = []
    first = 1
    last_exposure = 0
    for i in range(len(lats)):

        temp_counter = 0
        
        for j in range(times[i]-n*dt, times[i]+(n+1)*dt, dt):

            temp_counter += 1

            latitude, longitude, tle_date = getLatLong(int(j))
            anom_lats.append(latitude)
            anom_lons.append(longitude)
            anom_times.append(j)

    # find the closest point to the anomaly in each orbit
    for g in range(0, 3):

        i = t
        best_time = 0
        best_would_be_pxl_count = 0
        max_pxl_count = 0
        max_time = 0
        max_lat = 0
        max_lon = 0
        are_in = False

        in_first = False
        in_second = False 

        exposure_in_first = False

        orbit_counter = 0

        while i <= t_end:

            latitude, longitude, tle_date = getLatLong(int(i))

            fut_latitude, fut_longitude, fut_tle_date = getLatLong(i+step_size)

            if (g == 0):
                if i > t: 
                    if (dist(orbit_line_lats[-1], orbit_line_lons[-1], latitude, longitude) > 2.0):
                        orbit_line_lats.append(latitude)
                        orbit_line_lons.append(longitude)
                else:
                    orbit_line_lats.append(latitude)
                    orbit_line_lons.append(longitude)

            if latitude < 0 and fut_latitude > 0:
                orbit_counter += 1

            if not are_in:

                # we are not in the equator belt
                if abs(latitude) > (90 - (2*approx_pole + 1)):

                    # we enter from the equator belt
                    if (((latitude > (-90 + 2*approx_pole)) and (fut_latitude < (-90 + 2*approx_pole))) or ((latitude < (90 - 2*approx_pole)) and (fut_latitude > (90 - 2*approx_pole)))):

                        are_in = True
                        in_first = True
                        in_second = False
                        max_pxl_count = 0
                        best_would_be_pxl_count = 0
                        best_time = 0
                        print("Entered the first: latitude: {}, longitude: {}".format(latitude, longitude))

                    elif ((latitude > (90 - latitude_limit)) or (latitude < (-90 + latitude_limit))):

                        are_in = True
                        in_second = True
                        in_first = False
                        max_pxl_count = 0
                        best_would_be_pxl_count = 0
                        best_time = 0
                        print("Entered the second: latitude: {}, longitude: {}".format(latitude, longitude))

            if are_in:

                # times.append(i)
                # orbits.append(orbit_n)

                pxl_count = doses_rbf_log[int(math.floor(mesh_size*((longitude+180)/360))), int(math.floor(mesh_size*((latitude+90)/180)))]

                # we left the area
                # if (((latitude > 0) and (latitude > (90 - latitude_limit))) or ((latitude < 0) and (latitude < (-90 + latitude_limit)))):

                if in_first:

                    if (((latitude > 0) and (latitude > (90 - latitude_limit))) or ((latitude < 0) and (latitude < (-90 + latitude_limit)))):

                        are_in = False
                        in_first = False

                        if best_time > 1:

                            if add(max_lat, max_lon, best_time, orbit_counter):

                                print("Appending: latitude: {}, longitude: {}".format(max_lat, max_lon))
                                exposure_in_first = True
                        
                            else:

                                print("Could not add the point, too close.")
                                exposure_in_first = False

                        else:
                            exposure_in_first = False

                        max_pxl_count = 0
                        best_would_be_pxl_count = 0
                        best_time = 0

                        print("Left first: latitude: {}, longitude: {}".format(latitude, longitude))

                elif in_second:

                    if (abs(latitude - (90 - 2*approx_pole)) < 1) or (abs(latitude - (-90 + 2*approx_pole)) < 1):

                        are_in = False
                        in_second = False

                        # if not exposure_in_first:

                        #     if best_time > 1:

                        #         if add(max_lat, max_lon, best_time, orbit_counter):

                        #             print("Apending: latitude: {}, longitude: {}".format(max_lat, max_lon))

                        #         else:

                        #             print("Could not add the point, too close.")

                        max_pxl_count = 0
                        best_would_be_pxl_count = 0
                        best_time = 0

                        print("Left second: latitude: {}, longitude: {}".format(latitude, longitude))

                if pxl_count > best_would_be_pxl_count:

                    best_would_be_pxl_count = pxl_count

                if pxl_count > max_pxl_count:

                    if is_free(latitude, longitude):

                        if (pxl_count+1.5) >= best_would_be_pxl_count:

                            if (dist(latitude, longitude, anomaly_lat, anomaly_long) > anomaly_size) and (dist(latitude, longitude, sgap_lat, sgap_long) > sgap_size):

                                max_pxl_count = pxl_count
                                best_time = i
                                max_lat = latitude
                                max_lon = longitude
                                print("Found max: latitude: {}, longitude: {}, value: {}".format(latitude, longitude, pxl_count))

            i += step_size

# scan the surroundigs of the locations

    for z in range(len(anom_times)):

        times.append(anom_times[z])

    times.sort()
    list(set(times))

    out_lats = []
    # out_orbits = []
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
            file.write(time+"\tP\tx sp 400 1 70 0 1 {} 80 0 0\r\n".format(1+2+32))
            # time = datetime.datetime.utcfromtimestamp(t_now-50-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
            # file.write(time+"\tP\th conf 3 3 0 01400000000000000000\r\n")
            
        # time = datetime.datetime.utcfromtimestamp(t_now-hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
        # file.write(time+"\tP\th go 3 1\r\n")
        
        latitude, longitude, tle_date = getLatLong(int(t_now))
        out_lats.append(latitude)
        # out_orbits.append(orbits[i])
        out_lons.append(longitude)
        out_times.append(t_now)
        pxl_count = doses_rbf_lin[int(math.floor(mesh_size*(latitude+90)/180)), int(math.floor(mesh_size*(longitude+180)/360))]
        if pxl_count < 0:
            pxl_count = 0
        out_pxl_counts.append(pxl_count)

        if pxl_count > 0:
            desired_exposure = int(round(1000.0/(pxl_count/desired_fill)))
        else:
            desired_exposure = 1000*max_exposure

        if desired_exposure == 0:
            desired_exposure = 1

        if desired_exposure > 1000*max_exposure:
            desired_exposure = max_exposure*1000

        total_chunks += 16+1+(round(((desired_exposure/1000.0)*pxl_count)/20))+1

        # time = datetime.datetime.utcfromtimestamp(t_now-30).strftime('%Y-%m-%d %H:%M:%S')
        # file.write(time+"\t\tx in\r\n")

        if desired_exposure != last_exposure:
          time = datetime.datetime.utcfromtimestamp(t_now-15).strftime('%Y-%m-%d %H:%M:%S')
          file.write(time+"\t\tx se {}\r\n".format(desired_exposure))
          last_exposure = desired_exposure

        time = datetime.datetime.utcfromtimestamp(t_now-10).strftime('%Y-%m-%d %H:%M:%S')
        file.write(time+"\t\tx m\r\n")

        print("latitude: {}, longitude: {}, intensity: {}".format(latitude, longitude, pxl_count))

        # time = datetime.datetime.utcfromtimestamp(t_now+hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
        # file.write(time+"\tP\th stop 3 1\r\n")

    time = datetime.datetime.utcfromtimestamp(out_times[-1]+300).strftime('%Y-%m-%d %H:%M:%S')
    file.write(time+"\tP\tx pwr 0\r\n")
    time = datetime.datetime.utcfromtimestamp(out_times[-1]+300+hkc_buffer_time).strftime('%Y-%m-%d %H:%M:%S')
    
fig1 = []

def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    # ax1 = plt.subplot2grid((1, 1), (0, 0))

    #{ map
    
    m = createMap('cyl')
    
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)
    
    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    
    cb = m.colorbar(location="bottom", label="Log of relative intensity [px flux]") # draw colorbar
    
    for i in range(len(orbit_line_lats)):
        x, y = m(orbit_line_lons[i], orbit_line_lats[i])
        m.scatter(x, y, 20, marker='o', color='grey', zorder=5)
    
    for i in range(len(out_lats)):
        x, y = m(out_lons[i], out_lats[i])
        m.scatter(x, y, 80, marker='o', color='k', zorder=10)
    
        # plt.text(x+1, y+1, '{}'.format(out_orbits[i]), fontsize=13, fontweight='bold', ha='left', va='bottom', color='k', zorder=10)
    
    # cb.set_label('log10('+x_label+') '+x_units)
    plt.title('Combined scanning, starting on {}'.format(from_time))
    
    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)
    
    plt.savefig(directory+"/{}_combined.jpg".format(from_time).replace(' ', '_').replace(':', '_'), dpi=60, bbox_inches='tight')
    
    #} end of globe south

    ax1 = plt.subplot2grid((3, 2), (2, 0))

    #{ globe south
    
    m = createMap('ortho', -90, 0)
    
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)
    
    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    
    cb = m.colorbar(location="bottom", label="") # draw colorbar
    
    # for i in range(len(orbit_line_lats)):
    #     x, y = m(orbit_line_lons[i], orbit_line_lats[i])
    #     m.scatter(x, y, 20, marker='o', color='grey', zorder=5)
    
    for i in range(len(out_lats)):
        x, y = m(out_lons[i], out_lats[i])
        m.scatter(x, y, 80, marker='o', color='k', zorder=10)
    
        # plt.text(x+1, y+1, '{}'.format(out_orbits[i]), fontsize=13, fontweight='bold', ha='left', va='bottom', color='k', zorder=10)
    
    # cb.set_label('log10('+x_label+') '+x_units)
    # plt.title('Anomaly scanning, starting at {}'.format(from_time))
    
    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)
    
    # plt.savefig(directory+"/{}_anomaly.jpg".format(from_time).replace(' ', '_').replace(':', '_'), dpi=60, bbox_inches='tight')
    
    #} end of globe south

    ax1 = plt.subplot2grid((3, 2), (2, 1))

    #{ globe south
    
    m = createMap('ortho', +90, 0)
    
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)
    
    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    
    cb = m.colorbar(location="bottom", label="") # draw colorbar
    
    # for i in range(len(orbit_line_lats)):
    #     x, y = m(orbit_line_lons[i], orbit_line_lats[i])
    #     m.scatter(x, y, 20, marker='o', color='grey', zorder=5)
    
    for i in range(len(out_lats)):
        x, y = m(out_lons[i], out_lats[i])
        m.scatter(x, y, 80, marker='o', color='k', zorder=10)
    
        # plt.text(x+1, y+1, '{}'.format(out_orbits[i]), fontsize=13, fontweight='bold', ha='left', va='bottom', color='k', zorder=10)
    
    # cb.set_label('log10('+x_label+') '+x_units)
    # plt.title('Anomaly scanning, starting at {}'.format(from_time))
    
    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)
    
    # plt.savefig(directory+"/{}_anomaly.jpg".format(from_time).replace(' ', '_').replace(':', '_'), dpi=60, bbox_inches='tight')
    
    #} end of globe south

    plt.show()

print("total_chunks: {}".format(total_chunks))

file_name = directory+"/{}_combined.meta.txt".format(from_time).replace(' ', '_').replace(':', '_')

with open(file_name, "w") as file:

    file.write("from: "+from_time+"\r\n")
    file.write("to: "+to_time+"\r\n")
    file.write("desired fill: {} px per image\r\n".format(desired_fill))
    file.write("estimated number of chunks: {}\r\n".format(int(total_chunks)))
    # file.write("based on data range: {} to {}\r\n".format(from_idx, to_idx))
    file.write("max blunt exposure time: {} ms".format(max_exposure))

pid = os.fork()
if pid == 0:
    plot_everything()
