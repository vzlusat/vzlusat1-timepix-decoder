#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

import matplotlib.patches as patches # for plotting rectangles in the custom histogram

from include.baseMethods import *

from_idx = 28213
to_idx = 33000
outliers=[]

pcolor_min = 0
pcolor_max = 6

small_plot = 0

date_range = ''
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
epsilon=5.0

# prepare data
images = loadImageRange(from_idx, to_idx, 1, 0, 1, outliers)

n_bins = 1
bin_size = 150

bins = calculateImageHist(images, bin_size, n_bins)

print("dataset sizelen(bins[0]): {}".format(len(bins[0])))

bins_log = []

for idx,binn in enumerate(bins):
    doses_log = np.where(binn > 0, np.log10(binn), binn)
    bins_log.append(doses_log)

lats_orig, lons_orig = extractPositions(images)

bins_wrapped = []
bins_log_wrapped = []
for idx in range(n_bins):

    print("wrapping aroung bin: {}".format(idx))

    doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(bins[idx], lats_orig, lons_orig)
    doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(bins_log[idx], lats_orig, lons_orig)

    bins_wrapped.append(doses_wrapped)
    bins_log_wrapped.append(doses_log_wrapped)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

bins_rbf_lin = []
bins_rbf_log = []

for idx in range(n_bins):

    print("interpolating bin: {}".format(idx))

    # calculate RBF from log data
    rbf_lin = Rbf(lats_wrapped, lons_wrapped, bins_wrapped[idx], function='multiquadric', epsilon=epsilon, smooth=1)
    doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

    bins_rbf_lin.append(doses_rbf_lin)

    # calculate RBF from lin data
    rbf_log = Rbf(lats_wrapped, lons_wrapped, bins_log_wrapped[idx], function='multiquadric', epsilon=epsilon, smooth=1)
    doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

    bins_rbf_log.append(doses_rbf_log)

#} end of RBF interpolation

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    ax3 = plt.subplot2grid((1, 1), (0, 0))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    # m.pcolor(x_m_meshgrid, y_m_meshgrid, bins_rbf_log[idx], cmap=my_cm)
    m.pcolor(x_m_meshgrid, y_m_meshgrid, bins_rbf_log[0], cmap=my_cm, edgecolor=(1.0, 1.0, 1.0, 0.3), linewidth=0.005)

    cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar

    low_limit = idx*bin_size
    high_limit = (idx+1.0)*bin_size

    if idx == (n_bins - 1):
        high_limit = 150

    plt.title('X-ray/gamma {}-{} kev'.format(low_limit, high_limit), fontsize=13)

    x_m, y_m = m(lons_orig, lats_orig) # project points

    cb.set_label('log10('+x_label+') '+x_units)

    for image in images:
        latitude, longitude, tle_date = getLatLong(image.time)
        x, y = m(longitude, latitude)
        m.scatter(x, y, 0.2, marker='o', color='grey', zorder=10)

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.2, hspace=0.3)

    #} end of Figure 1

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
