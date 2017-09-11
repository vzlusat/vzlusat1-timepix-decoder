#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
from copy import deepcopy

from include.baseMethods import *

d2_from_idx = 417
d2_to_idx = 796

d3_from_idx = 813
d3_to_idx = 994

d4_from_idx = 800
d4_to_idx = 1388

outliers=[849, 1148]

date_range = ''
x_units = '[pix/s]'
x_label = 'Aprox. relative dose'
general_label = 'Dosimetry, 510 km LEO, VZLUSAT-1'

# prepare data
d2_images = loadImageRange(d2_from_idx, d2_to_idx, 32, 0, 1, outliers)
d3_images = loadImageRange(d3_from_idx, d3_to_idx, 32, 0, 1, outliers)
d4_images = loadImageRange(d4_from_idx, d4_to_idx, 32, 0, 1, outliers)

d2_doses = calculateTotalPixelCount(d2_images)
d3_doses = calculateTotalPixelCount(d3_images)
d4_doses = calculateTotalPixelCount(d4_images)
d2_doses_log = np.where(d2_doses > 0, np.log(d2_doses), d2_doses)
d3_doses_log = np.where(d3_doses > 0, np.log(d3_doses), d3_doses)
d4_doses_log = np.where(d4_doses > 0, np.log(d4_doses), d4_doses)

d2_lats, d2_lons = extractPositions(d2_images)
d3_lats, d3_lons = extractPositions(d3_images)
d4_lats, d4_lons = extractPositions(d4_images)

d2_lats_original = d2_lats
d2_lons_original = d2_lons
d4_lats_original = d4_lats
d4_lons_original = d4_lons
d2_images_original = d2_images
d4_images_original = d4_images

d2_doses_subset = []
d2_images_subset = []

d2_subset_lats = numpy.zeros(len(d3_images))
d2_subset_lons = numpy.zeros(len(d3_images))

d4_doses_subset = []
d4_images_subset = []

d4_subset_lats = numpy.zeros(len(d3_images))
d4_subset_lons = numpy.zeros(len(d3_images))

#{ doses for d2
for i in range(len(d3_images)):

    # find the closest point in d2 to d3
    latitude, longitude, tle_date = getLatLong(d3_images[i].time)
    d2_idx = min(range(len(d2_images)), key=lambda j: numpy.sqrt(pow(d2_lats[j]-latitude, 2) + pow(d2_lons[j]-longitude, 2)))
    d4_idx = min(range(len(d4_images)), key=lambda j: numpy.sqrt(pow(d4_lats[j]-latitude, 2) + pow(d4_lons[j]-longitude, 2)))

    # calculate the exposure time in seconds
    d2_exposure = d2_images[d2_idx].exposure
    if d2_exposure <= 60000:
        d2_exposure = d2_exposure*0.001
    else:
        d2_exposure = 60 + d2_exposure%60000

    # calculate the doses base on counts
    total_dose = d2_images[d2_idx].original_pixels/d2_exposure

    d2_doses_subset.append(deepcopy(total_dose))
    d2_images_subset.append(deepcopy(d2_images[d2_idx]))
    d2_subset_lats[i] = deepcopy(d2_lats[d2_idx])
    d2_subset_lons[i] = deepcopy(d2_lons[d2_idx])

    d2_images.remove(d2_images[d2_idx])
    d2_lats = np.delete(d2_lats, d2_idx)
    d2_lons = np.delete(d2_lons, d2_idx)

    # calculate the exposure time in seconds
    d4_exposure = d4_images[d4_idx].exposure
    if d4_exposure <= 60000:
        d4_exposure = d4_exposure*0.001
    else:
        d4_exposure = 60 + d4_exposure%60000

    # calculate the doses base on counts
    total_dose = d4_images[d4_idx].original_pixels/d4_exposure

    d4_doses_subset.append(total_dose)
    d4_images_subset.append(d4_images[d4_idx])
    d4_subset_lats[i] = d4_lats[d4_idx]
    d4_subset_lons[i] = d4_lons[d4_idx]

    d4_images.remove(d4_images[d4_idx])
    d4_lats = np.delete(d4_lats, d4_idx)
    d4_lons = np.delete(d4_lons, d4_idx)

    if d3_images[i].original_pixels > 50000:
        print("d3_images.id: {}".format(d3_images[i].id))

d2_doses_subset = np.array(d2_doses_subset)
d2_doses_subset_log = np.where(d2_doses_subset > 0, np.log(d2_doses_subset), d2_doses_subset)

d4_doses_subset = np.array(d4_doses_subset)
d4_doses_subset_log = np.where(d4_doses_subset > 0, np.log(d4_doses_subset), d4_doses_subset)
#}

#{ RBF interpolation

d2_doses_subset_log_wrapped, d2_subset_lats_wrapped, d2_subset_lons_wrapped = wrapAround(d2_doses_subset_log, d2_subset_lats, d2_subset_lons)
d4_doses_subset_log_wrapped, d4_subset_lats_wrapped, d4_subset_lons_wrapped = wrapAround(d4_doses_subset_log, d4_subset_lats, d4_subset_lons)

d2_doses_log_wrapped, d2_lats_wrapped, d2_lons_wrapped = wrapAround(d2_doses_log, d2_lats_original, d2_lons_original)
d4_doses_log_wrapped, d4_lats_wrapped, d4_lons_wrapped = wrapAround(d4_doses_log, d4_lats_original, d4_lons_original)

# create meshgrid for RBF
x_meshgrid, y_meshgrid = createMeshGrid(100)

# calculate RBF from lin data
d2_subset_rbf_log = Rbf(d2_subset_lats_wrapped, d2_subset_lons_wrapped, d2_doses_subset_log_wrapped, function='multiquadric', epsilon=0.1, smooth=1)
d2_subset_doses_rbf_log = d2_subset_rbf_log(x_meshgrid, y_meshgrid)

d2_rbf_log = Rbf(d2_lats_wrapped, d2_lons_wrapped, d2_doses_log_wrapped, function='multiquadric', epsilon=0.1, smooth=1)
d2_doses_rbf_log = d2_rbf_log(x_meshgrid, y_meshgrid)

d4_subset_rbf_log = Rbf(d4_subset_lats_wrapped, d4_subset_lons_wrapped, d4_doses_subset_log_wrapped, function='multiquadric', epsilon=0.1, smooth=1)
d4_subset_doses_rbf_log = d4_subset_rbf_log(x_meshgrid, y_meshgrid)

d4_rbf_log = Rbf(d4_lats_wrapped, d4_lons_wrapped, d4_doses_log_wrapped, function='multiquadric', epsilon=0.1, smooth=1)
d4_doses_rbf_log = d4_rbf_log(x_meshgrid, y_meshgrid)

d3_rbf_log = Rbf(d3_lats, d3_lons, d3_doses_log, function='multiquadric', epsilon=0.1, smooth=1)
d3_doses_rbf_log = d3_rbf_log(x_meshgrid, y_meshgrid)

#} end of RBF interpolation

def plot_everything(*args):

    plt.figure(1)

    #{ Figure 1

    #{ d2

    ax1 = plt.subplot2grid((3, 3), (0, 0))

    m = createMap('cyl')

    x_m, y_m = m(d2_subset_lons, d2_subset_lats) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(d2_doses_subset), bins='log', gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    cb.set_label('log10('+x_label+') '+x_units)
    plt.title(general_label+', '+date_range, fontsize=13)

    ax1 = plt.subplot2grid((3, 3), (1, 0))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, d2_subset_doses_rbf_log, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

    ax1 = plt.subplot2grid((3, 3), (2, 0))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, d2_doses_rbf_log, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

    #} end d2

    #{ d3

    ax1 = plt.subplot2grid((3, 3), (0, 1))

    m = createMap('cyl')

    x_m, y_m = m(d3_lons, d3_lats) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(d3_doses), bins='log', gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    cb.set_label('log10('+x_label+') '+x_units)
    plt.title(general_label+', '+date_range, fontsize=13)

    ax1 = plt.subplot2grid((3, 3), (1, 1))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, d3_doses_rbf_log, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

    #} end d3

    #{ d4

    ax1 = plt.subplot2grid((3, 3), (0, 2))

    m = createMap('cyl')

    x_m, y_m = m(d4_subset_lons, d4_subset_lats) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(d4_doses_subset), bins='log', gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    cb.set_label('log10('+x_label+') '+x_units)
    plt.title(general_label+', '+date_range, fontsize=13)

    ax1 = plt.subplot2grid((3, 3), (1, 2))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, d4_subset_doses_rbf_log, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

    ax1 = plt.subplot2grid((3, 3), (2, 2))

    m = createMap('cyl')

    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, d4_doses_rbf_log, cmap=my_cm)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    cb.set_label('log10('+x_label+') '+x_units)
    plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

    #} end d4

    plt.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.1, hspace=0.2)

    #} end of Figure 1

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
