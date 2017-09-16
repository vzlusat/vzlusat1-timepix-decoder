#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_idx = 385
to_idx = 2000
outliers=[1148]

pcolor_min = 0
pcolor_max = 7

small_plot = 1

date_range = 'all time'
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = 'Dosimetry 510 km LEO, VZLUSAT-1'

# prepare data
images = loadImageRange(from_idx, to_idx, 32, 1, 1, outliers)

doses = calculateEnergyDose(images)
doses_log = np.where(doses > 0, np.log10(doses), doses)

lats_orig, lons_orig = extractPositions(images)

doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

#} end of RBF interpolation

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    ax1 = plt.subplot2grid((2, 3), (0, 0))

#{ log-scale scatter

    m = createMap('cyl')

    x_m, y_m = m(lons_orig, lats_orig) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(doses), bins='log', gridsize=64, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10, vmin=pcolor_min, vmax=pcolor_max)
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
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

#} end of log-scale rbf

    ax3 = plt.subplot2grid((2, 3), (0, 2))

#{ linear rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_lin, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, '+date_range, fontsize=13)

#} end of linear rbf

    ax3 = plt.subplot2grid((2, 3), (1, 0))

#{ south-pole, log rbf

    m = createMap('ortho', -90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, '+date_range, fontsize=13)

#} end of south-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 1))

#{ north-pole, log rbf

    m = createMap('ortho', 90, 0)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, '+date_range, fontsize=13)

#} end of north-pole, log rbf

    ax3 = plt.subplot2grid((2, 3), (1, 2))

#{ anomaly, log rbf

    m = createMap('ortho', -30, -50)

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label(x_label+' '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, '+date_range, fontsize=13)

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
        plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

        #} end of log-scale rbf

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
