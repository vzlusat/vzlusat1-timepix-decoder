#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

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

image_bin_path = "../images_bin/"

from_idx = 405
to_idx = 1000

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
            images.append(new_image)
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

    doses.append(total_dose)

# create the map plot
plt.figure(1)
# plt.subplot(121)
# m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
# m = Basemap(projection='moll',lon_0=0,resolution='c')
m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c')

# draw continents
m.drawcoastlines()
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
CS = m.hexbin(x1, y1, C=numpy.array(doses), bins='log', gridsize=20, cmap=my_cmap, mincnt=0, zorder=10)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Pixel counts)')
plt.title('Radiation map in 450 km SSO LEO orbit', fontsize=13)

plt.show()

# plt.subplot(122)
# m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c')

# # draw continents
# m.drawcoastlines()
# m.drawparallels(np.arange(-90.,91.,30.))
# m.drawmeridians(np.arange(-180.,181.,60.))
# m.drawmapboundary(fill_color='white')

# lats = np.reshape(lats, (len(lats), 1))
# lons = np.reshape(lons, (len(lons), 1))
# points = np.hstack((lats, lons))
# print("np.shape(points): {}".format(np.shape(points)))
# grid_x, grid_y = np.mgrid[(-1.57):1:1.57j, (-3.14):1:3.14j]
# print("grid_x: {}".format(grid_x))
# # grid_z2 = griddata(points, doses, (grid_x, grid_y), method='cubic')

# # print("grid_z2: {}".format(grid_z2))

# tck = interpolate.bisplrep(lats, lons, np.array(doses), s=0)
# znew = interpolate.bisplev(grid_x[:,0], grid_y[0,:], tck)

# # x1, y1 = m(xnew, ynew)

# print("x1: {}".format(np.shape(x1)))
# print("x1: {}".format(np.shape(y1)))
# print("x1: {}".format(np.shape(np.array(doses))))

# u = np.linspace(0, 1, 10)
# print("u: {}".format(np.shape(u)))

# # m.pcolormesh(x1, y1, np.array(doses))

# plt.show()

# # x = np.arange(-5.01, 5.01, 0.25)
# # y = np.arange(-5.01, 5.01, 0.25)
# # xx, yy = np.meshgrid(x, y)
# # z = np.sin(xx**2+yy**2)
# # f = interpolate.interp2d(x, y, z, kind='cubic')

# # xnew = np.arange(-5.01, 5.01, 1e-2)
# # ynew = np.arange(-5.01, 5.01, 1e-2)
# # znew = f(xnew, ynew)
# # plt.plot(x, z[0, :], 'ro-', xnew, znew[0, :], 'b-')
# # plt.show()
