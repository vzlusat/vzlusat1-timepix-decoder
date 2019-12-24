#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_to = numpy.array([
[36352, 36671], # 1st full res
[36672, 37034], # 2nd full res
[37103, 37862], # 3rd full res
[37863, 38587], # 4rd full res
[38604, 39191], # 5rd full res
[39194, 39958], # 6rd full res
])
outliers=[]

pcolor_min = 0
pcolor_max = 6

small_plot = 1

date_range = ''
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = 'Radiation dose, 500 km LEO, VZLUSAT-1'
epsilon=0.1

# prepare data
images = loadImageRangeMulti(from_to, 1, 1, 1, outliers)

doses = calculateEnergyDose(images)
# doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

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

long_counts = []
short_counts = []
for idx,image in enumerate(images):
    if image.got_metadata:

        if image.exposure > 500:
            long_counts.append(image.original_pixels)
        else:
            short_counts.append(image.original_pixels)

tolerance = 3
percentile_long = 1 - (float(tolerance)/len(long_counts))
percentile_short = 1 - (float(tolerance)/len(short_counts))

long_perc_end = np.percentile(long_counts, percentile_long*100.0)
short_perc_end = np.percentile(short_counts, percentile_short*100.0)

long_median = np.percentile(long_counts, 50)
short_median = np.percentile(short_counts, 50)

print("long {:.2f}%: {}, {} images".format(percentile_long, long_perc_end, (1-percentile_long)*len(long_counts)))
print("short {:.2f}%: {}, {} images".format(percentile_short, short_perc_end, (1-percentile_short)*len(short_counts)))

print("long {:.2f}%: {}".format(50, long_median))
print("short {:.2f}%: {}".format(50, short_median))

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
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of linear rbf

    ax3 = plt.subplot2grid((2, 3), (1, 0))

#{ south-pole, log rbf

    m = createMap('ortho', -90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of south-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 1))

#{ north-pole, log rbf

    m = createMap('ortho', 90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps={}), linear scale, '.format(epsilon)+date_range, fontsize=13)

#} end of north-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 2))

#{ anomaly, log rbf

    m = createMap('ortho', -30, -50)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
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
        plt.title('Radiation dose, 500 km Low-Earth Orbit, VZLUSAT-1, '.format(epsilon)+date_range, fontsize=13)

        #} end of log-scale rbf

    plt.figure(3)

    plt.hist(long_counts, 20)
    plt.title('Long')

    plt.figure(4)

    plt.hist(short_counts, 20)
    plt.title('Short')

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
