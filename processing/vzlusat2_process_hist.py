#!/usr/bin/python3

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import csv
import calendar, datetime, time

from include.baseMethods import *

tle1, tle2, tle_time = initializeTLE("tle2.txt")

def utc2epoch(timestamp):
    epoch = time.mktime((datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")).timetuple()) + 3600*4
    return epoch

pcolor_min = 0
pcolor_max = 4

small_plot = 0

date_range = ''
x_units = '[-]'
x_label = 's_filt0 / exposure'
general_label = ''
epsilon=0.1

time_stamps = []
exposures = []
doses = []

# parse the file

with open('vzlusat2/june22a-exp1.txt') as csvfile:

    reader = csv.reader(csvfile, delimiter=',', quotechar='|')

    next(reader)

    for row in reader:
        time_stamps.append(row[1])
        exposures.append(float(row[2]))
        # doses.append(float(row[13]))
        doses.append(float(row[9]))

doses = np.array(doses)
exposures = np.array(exposures)

# obtain coordinates

lats_orig = []
lons_orig = []
epochs = []

for time_stamp in time_stamps:

    epoch = utc2epoch(time_stamp)

    epochs.append(epoch)

    latitude, longitude, tle_date = getLatLong(epoch, tle1, tle2, tle_time)
    print("tle_date: {}".format(tle_date))

    lats_orig.append(latitude)
    lons_orig.append(longitude)

lats_orig = np.array(lats_orig)
lons_orig = np.array(lons_orig)

print("epochs[0]: {}".format(epochs[0]))

# normalize the doses

for i in range(0, len(doses)):
    doses[i] = doses[i] / exposures[i]
    # doses[i] = doses[i]

# logaritm of doses

doses_log = np.where(doses > 0, np.log10(doses), doses)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=1.0, smooth=1)
doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=1.0, smooth=1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

#} end of RBF interpolation

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    ax1 = plt.subplot2grid((2, 3), (0, 0))

#{ log-scale scatter

    m = createMap('cyl')

    x_m, y_m = m(lons_orig, lats_orig) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(doses), bins='log', gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10, vmin=pcolor_min, vmax=pcolor_max)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    cb.set_label('log10('+x_label+') '+x_units)
    plt.title(general_label+', '+date_range, fontsize=13)

#} end of log-scale scatter

    ax2 = plt.subplot2grid((2, 3), (0, 1))

#{ log-scale rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), log10 scale, '.format(epsilon)+date_range, fontsize=13)

#} end of log-scale rbf

    ax3 = plt.subplot2grid((2, 3), (0, 2))

#{ linear rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_lin, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of linear rbf

    ax3 = plt.subplot2grid((2, 3), (1, 0))

#{ south-pole, log rbf

    m = createMap('ortho', -90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of south-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 1))

#{ north-pole, log rbf

    m = createMap('ortho', 90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of north-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 2))

#{ anomaly, log rbf

    m = createMap('ortho', -30, -50)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of anomaly, log rbf

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.1)

    #} end of Figure 1

    if small_plot:

        plt.figure(2)

        ax2 = plt.subplot2grid((1, 1), (0, 0))

        #{ log-scale rbf

        m = createMap('cyl')

        x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

        m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

        cb = m.colorbar(location="bottom", label="Z") # draw colorbar
        cb.set_label('log10('+x_label+') '+x_units)
        plt.title('RBF multiquadric (eps={}), log10 scale, '.format(epsilon)+date_range, fontsize=13)

        #} end of log-scale rbf

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
