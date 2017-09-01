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

image_bin_path = "../images_bin/"

from_idx = 385
to_idx = 796

# the number of image in the first dosimetry
dosimetry_1_n = 42

# prepare arrays
images = []
doses = []

# load images
for i in range(from_idx, to_idx):

    # for count mode only
    # load anything that has metadata and any data, so presumably it is a proper image
    new_image = loadImage(i, 1, image_bin_path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 2, image_bin_path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 4, image_bin_path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 8, image_bin_path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 16, image_bin_path)
    if new_image == 0 or new_image.got_data == 0 or new_image.got_metadata == 0:
        new_image = loadImage(i, 32, image_bin_path)

    # # use the image only if we got data
    # if new_image != 0 and new_image.got_data == 1:
    #     images.append(new_image)

    # use the image only when we got metadata
    if new_image != 0 and new_image.got_metadata == 1:
        images.append(new_image)

# calculate the doses in those images
for i in range(len(images)):

    # calculate the exposure time in seconds
    exposure = images[i].exposure
    if exposure <= 60000:
        exposure = exposure*0.001
    else:
        exposure = 60 + exposure%60000

    # calculate the doses base on counts
    total_dose = images[i].original_pixels/exposure

    doses.append(total_dose)

# create the map plot
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

# reate artificial measurement in places, where data were not produced
# during the first dosimetry (scanning mode)
for i in range(dosimetry_1_n):

    time = 1503686482+i*300
    latitude, longitude, tle_date = getLatLong(time)
    lats[i+len(images)] = latitude
    lons[i+len(images)] = longitude
    doses.append(30)

# project lats and long to the map coordinates
x1, y1 = m(lons, lats)

# mutate the colormap of a choice to be transparent at the low end
cmap = pl.cm.gist_heat_r
# get the original colormap colors
my_cmap = cmap(numpy.arange(cmap.N))
# set alpha
my_cmap[:,-1] = numpy.linspace(0.4, 1, cmap.N)
# create the new colormap
my_cmap = ListedColormap(my_cmap)

# make plot using hexbin
CS = m.hexbin(x1, y1, C=numpy.array(doses), bins='log', gridsize=18, cmap=my_cmap, mincnt=0, zorder=10)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10(Pixel counts)')
plt.title('Radiation map in 450 km SSO LEO orbit', fontsize=13)

plt.show()
