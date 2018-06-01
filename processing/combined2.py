#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_idx = 22535
to_idx = 22614
outliers=[]

pcolor_min = 0
pcolor_max = 7

small_plot = 0

date_range = ''
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = '#2 combined scanning'
epsilon=0.1

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 0, 1, outliers)

doses = calculateTotalPixelCount(images)
# doses = calculateTotalPixelCount(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='gaussian', epsilon=15, smooth=0)
doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='gaussian', epsilon=15, smooth=0)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

#} end of RBF interpolation

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    ax3 = plt.subplot2grid((1, 1), (0, 0))

#{ linear rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF gaussian (eps={}), log10 scale, '.format(epsilon)+date_range, fontsize=13)

    x_m, y_m = m(lons_orig, lats_orig) # project points

    # CS = m.hexbin(x_m, y_m, C=numpy.array(doses), bins='log', gridsize=16, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10, vmin=pcolor_min, vmax=pcolor_max)
    # cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    # cb.set_label('log10('+x_label+') '+x_units)

    for image in images:
        latitude, longitude, tle_date = getLatLong(image.time)
        x, y = m(longitude, latitude)
        m.scatter(x, y, 20, marker='o', color='k', zorder=10)

#} end of linear rbf

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
        plt.title('RBF gaussian (eps={}), log10 scale, '.format(epsilon)+date_range, fontsize=13)

        #} end of log-scale rbf

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
