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

from_idx = 417
to_idx = 796

# # the number of image in the first dosimetry
dosimetry_1_n = 0

# prepare arrays
images = []
doses = []

kevs = [3.6041, 5.32915, 8.40915, 13.51345, 20.67375, 29.2457, 38.5756, 48.2956, 58.22885, 68.28795, 78.4265, 88.61815, 98.84695, 109.1026, 119.37825, 129.6693]

# load images
for i in range(from_idx, to_idx):

    # for count mode only
    # load anything that has metadata and any data, so presumably it is a proper image
    new_image = loadImage(i, 32, image_bin_path)

    if new_image == 0:
        print("image {} could not be loaded".format(i))
    else:
        if new_image.got_metadata == 1:
            if new_image.got_data == 1:
                images.append(new_image)
            else:
                print("image {} does not have data".format(i))
        else:
            print("image {} does not have metadata".format(i))

# calculate the doses in those images
for i in range(len(images)):

    # calculate the exposure time in seconds
    exposure = images[i].exposure
    if exposure <= 60000:
        exposure = exposure*0.001
    else:
        exposure = 60 + exposure%60000

    # calculate the doses base on counts
    total_dose = np.sum(images[i].data*kevs)/exposure

    # if images[i].original_pixels > 10000:
    #     print("{} {}".format(images[i].id, images[i].original_pixels))

    doses.append(total_dose)

# create the map plot
plt.figure(1)
plt.subplot(131)
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
lats = numpy.zeros(len(images)+dosimetry_1_n)
lons = numpy.zeros(len(images)+dosimetry_1_n)

# decode lat and longs from tle
for i in range(len(images)):

    latitude, longitude, tle_date = getLatLong(images[i].time)
    lats[i] = latitude
    lons[i] = longitude

# # reate artificial measurement in places, where data were not produced
# # during the first dosimetry (scanning mode)
# for i in range(dosimetry_1_n):

#     time = 1503686482+i*300
#     latitude, longitude, tle_date = getLatLong(time)
#     lats[i+len(images)] = latitude
#     lons[i+len(images)] = longitude
#     doses.append(50)

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
CS = m.hexbin(x1, y1, C=numpy.array(doses), bins='log', gridsize=16, cmap=my_cmap, mincnt=0, reduce_C_function=np.max, zorder=10)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Total energy) [keV/s]')
plt.title('Measurements in 510 km LEO orbit', fontsize=13)

#################################################################################

n = 100

tlat = np.linspace(-90, 90, n)
tlon = np.linspace(-180, 180, n)

doses = np.array(doses)
doses_log = np.where(doses > 0, np.log(doses), doses)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(lats, lons, doses_log, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)

plt.subplot(132)

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

doses = np.array(doses)

XX, YY = np.meshgrid(tlat, tlon)
rbf = Rbf(lats, lons, doses, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)
ZZ = np.where(ZZ < 0, 0, ZZ)

plt.subplot(133)

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

# plt.subplot(133)

# m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

# # draw continents
# m.drawcoastlines()
# m.drawparallels(np.arange(-90.,91.,30.))
# m.drawmeridians(np.arange(-180.,181.,60.))
# m.drawmapboundary(fill_color='white')

# lats = np.reshape(lats, (len(lats), 1))
# lons = np.reshape(lons, (len(lons), 1))
# points = np.hstack((lats, lons))
# grid_z2 = griddata(points, doses, (XX, YY), method='cubic')

# m.imshow(grid_z2.T, extent=(0, 1, 0, 1), origin='lower', cmap=my_cmap)

# cb = m.colorbar(location="bottom", label="Z") # draw colorbar
# cb.set_label('Total energy [keV]')
# plt.title('Cubic interpolation, linear scale', fontsize=13)

plt.show()
