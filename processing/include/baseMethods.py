from mpl_toolkits.basemap import Basemap

# for modifying existing colormap to be transparent
import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap

# to also allow loading from a parent directory
import sys
sys.path.append('../')

from src.loadImage import *
from src.Image import *

import numpy as np
import math

image_bin_path = "../images_bin/"

kevs = [3.6041, 5.32915, 8.40915, 13.51345, 20.67375, 29.2457, 38.5756, 48.2956, 58.22885, 68.28795, 78.4265, 88.61815, 98.84695, 109.1026, 119.37825, 129.6693]

from src.tle import *
parseTLE()

def colormapToTransparent(original):

    # mutate the colormap of a choice to be transparent at the low end
    cmap = original
    # get the original colormap colors
    my_cmap = cmap(numpy.arange(cmap.N))
    # set alpha
    my_cmap[:,-1] = numpy.linspace(0.1, 1, cmap.N)
    # create the new colormap
    my_cmap = ListedColormap(my_cmap)

    return my_cmap

def dist(x1, y1, x2, y2):

    return math.sqrt(math.pow(x2-x1, 2)+math.pow(y2-y1, 2))

# prepare a transparent colormap
my_cm = colormapToTransparent(pl.cm.jet)
my_hot = colormapToTransparent(pl.cm.hot)

# formatting log scale lables
def fmt(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    b = int(b)
    return r'${}e{{{}}}$'.format(a, b)

def extractPositions(images):

    # prepare numpy arrays for the lats and longs
    lats = numpy.zeros(len(images))
    lons = numpy.zeros(len(images))

    # decode lat and longs from tle
    for i in range(len(images)):

        latitude, longitude, tle_date = getLatLong(images[i].time)

        if latitude == 0 and longitude == 0 and tle_date == 0:
            print("could not extract position from {}_{}".format(images[i].id, images[i].type))

        lats[i] = latitude
        lons[i] = longitude

    return lats, lons

# load reange of images having a particular type
def loadImageRange(from_idx, to_idx, image_type, require_data=0, require_metadata=0, outliers=[]):

    images = []

    # load images
    for i in range(from_idx, to_idx):

        try:
            dev_null = outliers.index(i)
            continue
        except:
            pass

        # for count mode only
        # load anything that has metadata and any data, so presumably it is a proper image
        new_image = loadImage(i, image_type, image_bin_path)

        if new_image == 0:
            print("image {} could not be loaded".format(i))
        else:
            if require_data and not new_image.got_data:
                print("image {} does not contain data".format(i))
                continue 

            if require_metadata and not new_image.got_metadata:
                print("image {} does not contain metadata".format(i))
                continue 

            images.append(new_image)

    return images

# calculate the doses in image range
def calculateEnergyDose(images):
    
    doses = []

    for i in range(len(images)):

        image_dose = 0

        if images[i].got_data == 0:
            print("Image {} got no data".format(images[i].id))
            continue

        # calculate the exposure time in seconds
        exposure = images[i].exposure
        if exposure <= 60000:
            exposure = exposure*0.001
        else:
            exposure = 60 + exposure%60000

        # calculate the doses base on counts
        image_dose = np.sum(images[i].data*kevs)/exposure

        doses.append(image_dose)

    return np.array(doses)

# calculate the doses in image range
def calculateTotalPixelCount(images):
    
    doses = []

    for i in range(len(images)):

        image_dose = 0

        if images[i].got_metadata == 0:
            print("Image {} got no metadata".format(images[i].id))
            continue

        # calculate the exposure time in seconds
        exposure = images[i].exposure
        if exposure <= 60000:
            exposure = exposure*0.001
        else:
            exposure = 60 + exposure%60000

        # calculate the doses base on counts
        image_dose = images[i].original_pixels/exposure

        doses.append(image_dose)

    return np.array(doses)

def createMap(projection, lat=0, lon=0):

    m = []

    if projection == 'ortho':
        m = Basemap(projection=projection, lat_0=lat, lon_0=lon, resolution='l')
    else:
        m = Basemap(projection=projection, lon_0=0, llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')

    # draw continents
    m.drawcoastlines()
    m.drawparallels(np.arange(-90, 91, 30))
    m.drawmeridians(np.arange(-180, 181, 60))
    m.drawmapboundary(fill_color='white')

    return m

def wrapAround(doses, lats, lons):

    doses_wide = np.concatenate([doses, doses, doses])
    lats_wide = np.concatenate([lats, lats, lats])
    lons_wide = np.concatenate([lons-360, lons, lons+360])

    return doses_wide, lats_wide, lons_wide

def createMeshGrid(n):

    tlat = np.linspace(-90, 90, n)
    tlon = np.linspace(-180, 180, n)

    XX, YY = np.meshgrid(tlat, tlon)

    return XX, YY
