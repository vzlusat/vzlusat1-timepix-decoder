#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

pre_from_idx = 1449
pre_to_idx = 1772
pre_outliers=[]

post_from_idx = 3758
post_to_idx = 4240
post_outliers=[]

pcolor_min = 0
pcolor_max = 8

small_plot = 0

date_range = '16-17.10.2017'
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = '9th dosimetry 510 km LEO, VZLUSAT-1'
epsilon=0.1

#{ PRE-openning data

# prepare data
pre_images = loadImageRange(pre_from_idx, pre_to_idx, 32, 1, 1, pre_outliers)

pre_doses = calculateEnergyDose(pre_images)
doses_log = np.where(pre_doses > 0, np.log10(pre_doses), pre_doses)

pre_lats_orig, pre_lons_orig = extractPositions(pre_images)

pre_doses_wrapped, pre_lats_wrapped, pre_lons_wrapped = wrapAround(pre_doses, pre_lats_orig, pre_lons_orig)
pre_doses_log_wrapped, pre_lats_wrapped, pre_lons_wrapped = wrapAround(doses_log, pre_lats_orig, pre_lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
pre_rbf_lin = Rbf(pre_lats_wrapped, pre_lons_wrapped, pre_doses_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
pre_doses_rbf_lin = pre_rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
pre_rbf_log = Rbf(pre_lats_wrapped, pre_lons_wrapped, pre_doses_log_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
pre_doses_rbf_log = pre_rbf_log(x_meshgrid, y_meshgrid)

#} end of POST-openning data

#} end of RBF interpolation

#{ POST-openning data

# prepare data
post_images = loadImageRange(post_from_idx, post_to_idx, 32, 1, 1, post_outliers)

post_doses = calculateEnergyDose(post_images)
doses_log = np.where(post_doses > 0, np.log10(post_doses), post_doses)

post_lats_orig, post_lons_orig = extractPositions(post_images)

post_doses_wrapped, post_lats_wrapped, post_lons_wrapped = wrapAround(post_doses, post_lats_orig, post_lons_orig)
post_doses_log_wrapped, post_lats_wrapped, post_lons_wrapped = wrapAround(doses_log, post_lats_orig, post_lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from log data
post_rbf_lin = Rbf(post_lats_wrapped, post_lons_wrapped, post_doses_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
post_doses_rbf_lin = post_rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
post_rbf_log = Rbf(post_lats_wrapped, post_lons_wrapped, post_doses_log_wrapped, function='multiquadric', epsilon=0.1, smooth=0)
post_doses_rbf_log = post_rbf_log(x_meshgrid, y_meshgrid)

#} end of POST-openning data

diff_doses_rbf_log = post_doses_rbf_log - pre_doses_rbf_log

#} end of RBF interpolation

# calculate the difference

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    ax1 = plt.subplot2grid((2, 2), (0, 0))

#{ log-scale rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, pre_doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), log10 scale, '.format(epsilon)+'18-19.9.2017', fontsize=13)

#} end of log-scale rbf


    ax2 = plt.subplot2grid((2, 2), (0, 1))

#{ log-scale rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, post_doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), log10 scale, '.format(epsilon)+'25-26.10.2017', fontsize=13)

#} end of log-scale rbf

    ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

#{ log-scale rbf

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, diff_doses_rbf_log, cmap=my_hot, vmin=pcolor_min, vmax=3)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps={}), log10 scale, intensity difference', fontsize=13)

#} end of log-scale rbf

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.15, hspace=0.15)

    #} end of Figure 1

    if small_plot:

        plt.figure(2)

        ax2 = plt.subplot2grid((1, 1), (0, 0))

        #{ log-scale rbf

        m = createMap('cyl')

        x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

        m.pcolor(x_m_meshgrid, y_m_meshgrid, post_doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

        cb = m.colorbar(location="bottom", label="Z") # draw colorbar
        cb.set_label('log10('+x_label+') '+x_units)
        plt.title('RBF multiquadric (eps={}), log10 scale, '.format(epsilon)+date_range, fontsize=13)

        #} end of log-scale rbf

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
