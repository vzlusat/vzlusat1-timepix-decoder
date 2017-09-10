#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from math import *
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker

# to also allow loading from a parent directory
import sys
sys.path.append('../')

from include.filtration import *
from src.loadImage import *
from src.Image import *

# for modifying existing colormap to be transparent
import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap

# we will need two-line elements
import datetime
from src.tle import *
parseTLE()

# interpolation
from scipy import interpolate
from scipy.interpolate import griddata

def fmt(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

image_bin_path = "../images_bin/"

d2_from_idx = 417
d2_to_idx = 796

d3_from_idx = 813
d3_to_idx = 1200

# prepare arrays
d3_images = []
d2_images = []
d2_images_subset = []

d2_doses_subset = []
d3_doses = []

d2_lats = []
d2_lons = []

d2_subset_lats = []
d2_subset_lons = []

kevs = [3.6041, 5.32915, 8.40915, 13.51345, 20.67375, 29.2457, 38.5756, 48.2956, 58.22885, 68.28795, 78.4265, 88.61815, 98.84695, 109.1026, 119.37825, 129.6693]

# load d2 images
for i in range(d2_from_idx, d2_to_idx):

    # for count mode only
    # load anything that has metadata and any data, so presumably it is a proper image
    new_image = loadImage(i, 32, image_bin_path)

    if new_image == 0:
        print("image {} could not be loaded".format(i))
    else:
        if new_image.got_metadata == 1:
            d2_images.append(new_image)
        else:
            print("image {} does not have metadata".format(i))

# prepare numpy arrays for the lats and longs
d2_lats = numpy.zeros(len(d2_images))
d2_lons = numpy.zeros(len(d2_images))

# decode lats and lons for d2 images
for i in range(len(d2_images)):

    latitude, longitude, tle_date = getLatLong(d2_images[i].time)
    d2_lats[i] = latitude
    d2_lons[i] = longitude

# load d3_images
for i in range(d3_from_idx, d3_to_idx):

    # for count mode only
    # load anything that has metadata and any data, so presumably it is a proper image
    new_image = loadImage(i, 32, image_bin_path)

    if new_image == 0:
        print("image {} could not be loaded".format(i))
    else:
        if new_image.got_metadata == 1:
            d3_images.append(new_image)
        else:
            print("image {} does not have metadata".format(i))

d2_subset_lats = numpy.zeros(len(d3_images))
d2_subset_lons = numpy.zeros(len(d3_images))

# calculate the doses in d2_images
for i in range(len(d3_images)):

    # calculate the exposure time in seconds
    exposure = d3_images[i].exposure
    if exposure <= 60000:
        exposure = exposure*0.001
    else:
        exposure = 60 + exposure%60000

    # find the closest point in d2 to d3
    latitude, longitude, tle_date = getLatLong(d3_images[i].time)
    idx = min(range(len(d2_images)), key=lambda i: numpy.sqrt(pow(d2_lats[i]-latitude, 2) + pow(d2_lons[i]-longitude, 2)))

    # calculate the doses base on counts
    total_dose = d2_images[idx].original_pixels/exposure

    d2_doses_subset.append(total_dose)
    d2_images_subset.append(d2_images[idx])
    d2_subset_lats[i] = latitude
    d2_subset_lons[i] = longitude

# calculate the doses in those d3_images
for i in range(len(d3_images)):

    # calculate the exposure time in seconds
    exposure = d3_images[i].exposure
    if exposure <= 60000:
        exposure = exposure*0.001
    else:
        exposure = 60 + exposure%60000

    # calculate the doses base on counts
    total_dose = d3_images[i].original_pixels/exposure

    d3_doses.append(total_dose)

# create the map plot

#{ Figure 1
plt.figure(1)
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
# m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
# m = Basemap(projection='moll',lon_0=0,resolution='c')
# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
# m.fillcontinents(color='coral',lake_color='aqua')
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

# prepare numpy arrays for the lats and longs
lats = numpy.zeros(len(d3_images))
lons = numpy.zeros(len(d3_images))

# decode lat and longs from tle
for i in range(len(d3_images)):

    latitude, longitude, tle_date = getLatLong(d3_images[i].time)
    lats[i] = latitude
    lons[i] = longitude

# project lats and long to the map coordinates
x1, y1 = m(lons, lats)

# mutate the colormap of a choice to be transparent at the low end
cmap = pl.cm.jet
# get the original colormap colors
my_cmap = cmap(numpy.arange(cmap.N))
# set alpha
my_cmap[:,-1] = numpy.linspace(0.1, 1, cmap.N)
# create the new colormap
my_cmap = ListedColormap(my_cmap)

# make plot using hexbin
CS = m.hexbin(x1, y1, C=numpy.array(d3_doses), bins='log', gridsize=32, cmap=my_cmap, mincnt=0, reduce_C_function=np.max, zorder=10)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Total energy) [keV/s]')
plt.title('Measurements in 510 km LEO orbit', fontsize=13)

#################################################################################

n = 100

tlat = np.linspace(-90, 90, n)
tlon = np.linspace(-180, 180, n)

d3_doses = np.array(d3_doses)
doses_log = np.where(d3_doses > 0, np.log(d3_doses), d3_doses)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(lats, lons, doses_log, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)

ax2 = plt.subplot2grid((2, 2), (1, 0))

# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
# m.fillcontinents(color='coral',lake_color='aqua')
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

new_x1, new_y1 = m(YY, XX)

m.pcolormesh(new_x1, new_y1, ZZ, cmap=my_cmap)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Total energy) [keV/s]')
plt.title('RBF multiquadric (eps=10e-1), log10 scale', fontsize=13)

##################################################################################

n = 100

tlat = np.linspace(-90, 90, n)
tlon = np.linspace(-180, 180, n)

d3_doses = np.array(d3_doses)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(lats, lons, d3_doses, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)
ZZ = np.where(ZZ < 0, 0, ZZ)

ax3 = plt.subplot2grid((2, 2), (1, 1))

# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

new_x1, new_y1 = m(YY, XX)

m.pcolormesh(new_x1, new_y1, ZZ, cmap=my_cmap)

cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
cb.set_label('Total energy [keV/s]')
plt.title('RBF multiquadric (eps=10e-1), linear scale', fontsize=13)

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.05)

#}

#{ Figure 2
plt.figure(2)
ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
# m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
# m = Basemap(projection='moll',lon_0=0,resolution='c')
# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
# m.fillcontinents(color='coral',lake_color='aqua')
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

# prepare numpy arrays for the lats and longs
lats = numpy.zeros(len(d2_images_subset))
lons = numpy.zeros(len(d2_images_subset))

# decode lat and longs from tle
for i in range(len(d2_images_subset)):

    latitude, longitude, tle_date = getLatLong(d2_images_subset[i].time)
    lats[i] = latitude
    lons[i] = longitude

# project lats and long to the map coordinates
x1, y1 = m(lons, lats)

# mutate the colormap of a choice to be transparent at the low end
cmap = pl.cm.jet
# get the original colormap colors
my_cmap = cmap(numpy.arange(cmap.N))
# set alpha
my_cmap[:,-1] = numpy.linspace(0.1, 1, cmap.N)
# create the new colormap
my_cmap = ListedColormap(my_cmap)

# make plot using hexbin
CS = m.hexbin(x1, y1, C=numpy.array(d2_doses_subset), bins='log', gridsize=32, cmap=my_cmap, mincnt=0, reduce_C_function=np.max, zorder=10)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Total energy) [keV/s]')
plt.title('Measurements in 510 km LEO orbit', fontsize=13)

#################################################################################

n = 100

tlat = np.linspace(-90, 90, n)
tlon = np.linspace(-180, 180, n)

d2_doses_subset = np.array(d2_doses_subset)
doses_log = np.where(d2_doses_subset > 0, np.log(d2_doses_subset), d2_doses_subset)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(d2_subset_lats, d2_subset_lons, doses_log, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)

ax2 = plt.subplot2grid((2, 2), (1, 0))

# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
# m.fillcontinents(color='coral',lake_color='aqua')
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

new_x1, new_y1 = m(YY, XX)

m.pcolormesh(new_x1, new_y1, ZZ, cmap=my_cmap)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Total energy) [keV/s]')
plt.title('RBF multiquadric (eps=10e-1), log10 scale', fontsize=13)

##################################################################################

n = 100

tlat = np.linspace(-90, 90, n)
tlon = np.linspace(-180, 180, n)

d2_doses_subset = np.array(d2_doses_subset)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(d2_subset_lats, d2_subset_lons, d2_doses_subset, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)
ZZ = np.where(ZZ < 0, 0, ZZ)

ax3 = plt.subplot2grid((2, 2), (1, 1))

# m = Basemap(projection='eck4', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
m = Basemap(projection='cyl', lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# draw continents
m.drawcoastlines()
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

new_x1, new_y1 = m(YY, XX)

m.pcolormesh(new_x1, new_y1, ZZ, cmap=my_cmap)

cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
cb.set_label('Total energy [keV/s]')
plt.title('RBF multiquadric (eps=10e-1), linear scale', fontsize=13)

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.05)

#}

plt.show()
