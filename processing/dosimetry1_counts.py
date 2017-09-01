#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from numpy.random import uniform

sys.path.append('../')

from include.filtration import *
from src.loadImage import *
from src.Image import *
from src.tle import *

parseTLE()

path = "../images_bin/"

# load the images
images = []

from_idx = 385
to = 796
fake = 42

for i in range(from_idx, to):

    new_image = loadImage(i, 1, path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 2, path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 4, path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 8, path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 16, path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 32, path)

    # if new_image != 0 and new_image.got_data == 1:
    #     images.append(new_image)

    if new_image != 0 and new_image.got_metadata == 1:
        images.append(new_image)

doses = []

kevs = [3.6041, 5.32915, 8.40915, 13.51345, 20.67375, 29.2457, 38.5756, 48.2956, 58.22885, 68.28795, 78.4265, 88.61815, 98.84695, 109.1026, 119.37825, 129.6693]

print("len(kevs): {}".format(len(kevs)))

for i in range(len(images)):

    exposure = images[i].exposure

    if exposure <= 60000:
        exposure = exposure*0.001
    else:
        exposure = 60 + exposure%60000

    suma = images[i].original_pixels/exposure
    print("suma: {}".format(suma))

    doses.append(suma)

# m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
# m = Basemap(projection='moll',lon_0=0,resolution='c')
m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c')

# m.fillcontinents(color='0.8')
# m.fillcontinents(lake_color='white')
m.drawcoastlines()
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,91.,30.))
m.drawmeridians(np.arange(-180.,181.,60.))
m.drawmapboundary(fill_color='white')

# number of points, bins to plot.
npts = len(images)+fake
bins = 14

# generate random points on a sphere,
# so that every small area on the sphere is expected
# to have the same number of points.
# http://mathworld.wolfram.com/SpherePointPicking.html
u = uniform(0.,1.,size=npts)
v = uniform(0.,1.,size=npts)
lons = 360.*u
lats = (180./np.pi)*np.arccos(2*v-1) - 90.
# toss points outside of map region.
# lats = np.compress(lats > 20, lats)
# lons = np.compress(lats > 20, lons)

lats = numpy.zeros(len(images)+fake)
lons = numpy.zeros(len(images)+fake)

for i in range(len(images)):

    latitude, longitude, tle_date = getLatLong(images[i].time)
    lats[i] = latitude
    lons[i] = longitude

import datetime
import re
import time

# fake the measurement that were not save, i.e. have been under 50 pixels
for i in range(fake):

    time = 1503686482+i*300
    latitude, longitude, tle_date = getLatLong(time)
    lats[i+len(images)] = latitude
    lons[i+len(images)] = longitude
    doses.append(30)
    print("time: {}".format(datetime.datetime.utcfromtimestamp(time)))

# convert to map projection coordinates.
x1, y1 = m(lons, lats)

# remove points outside projection limb.
# x = np.compress(np.logical_or(x1 < 1.e20, y1 < 1.e20), x1)
# y = np.compress(np.logical_or(x1 < 1.e20, y1 < 1.e20), y1)
# # function to plot at those points.
# xscaled = 4.*(x-0.5*(m.xmax-m.xmin))/m.xmax
# yscaled = 4.*(y-0.5*(m.ymax-m.ymin))/m.ymax
# z = xscaled*np.exp(-xscaled**2-yscaled**2)

# set up a linear colormap which is red and only changes alpha
# (1,0,0,1) --> (1,0,0,0) 

import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap

# Choose colormap
cmap = pl.cm.gist_heat_r

# Get the colormap colors
my_cmap = cmap(numpy.arange(cmap.N))

# Set alpha
my_cmap[:,-1] = numpy.linspace(0.4, 1, cmap.N)

# Create new colormap
my_cmap = ListedColormap(my_cmap)

# make plot using hexbin
# fig = plt.figure(figsize=(12,5))
# ax = fig.add_subplot(122)
CS = m.hexbin(x1, y1, C=numpy.array(doses), bins='log', gridsize=bins, cmap=my_cmap, mincnt=0, zorder=10)
# draw coastlines, lat/lon lines.
m.drawcoastlines(linewidth=0.25)
# m.drawcountries(linewidth=0.25)
# m.fillcontinents(color='coral', lake_color='aqua')
# draw the edge of the m projection region (the projection limb)
m.drawmapboundary(fill_color='white')
# draw lat/lon grid lines every 30 degrees.
# m.drawmeridians(numpy.arange(0,360,30))
# m.drawparallels(numpy.arange(-90,90,30))
cb = m.colorbar(location="bottom",label="Z") # draw colorbar
# plt.title('hexbin', fontsize=20)

cb.set_label('log10(Pixel counts)')

plt.title('Radiation map in 450 km SSO LEO orbit', fontsize=13)
plt.gcf().set_size_inches(10,10)
plt.show()
