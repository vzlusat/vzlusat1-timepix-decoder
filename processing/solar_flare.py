#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

pcolor_min = 0
pcolor_max = 8

small_plot = 1

date_range = '8-9.9.2017'
x_units = '(keV/s, log)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = '3rd dosimetry 510 km LEO, VZLUSAT-1'
epsilon=1.0

from_idx = 417
to_idx = 796
outliers=[]

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

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=epsilon, smooth=0.1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

plt.figure(1)

ax2 = plt.subplot2grid((1, 1), (0, 0))

m = createMap('cyl')

x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max, edgecolor=(1.0, 1.0, 1.0, 0.3), linewidth=0.01)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label(''+x_label+' '+x_units)

plt.show()

from_idx = 813
to_idx = 993

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

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=epsilon, smooth=0.1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

plt.figure(2)

ax2 = plt.subplot2grid((1, 1), (0, 0))

m = createMap('cyl')

x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max, edgecolor=(1.0, 1.0, 1.0, 0.3), linewidth=0.01)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label(''+x_label+' '+x_units)

plt.show()

from_idx = 994
to_idx = 1388
outliers=[1148]

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

# calculate RBF from lin data
rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=epsilon, smooth=0.1)
doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

plt.figure(3)

ax2 = plt.subplot2grid((1, 1), (0, 0))

m = createMap('cyl')

x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max, edgecolor=(1.0, 1.0, 1.0, 0.3), linewidth=0.01)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label(''+x_label+' '+x_units)

plt.show()
