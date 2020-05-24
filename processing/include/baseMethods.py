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

import copy

image_bin_path = "../images_bin/"

obc_time_offset_ = 946684800

kevs = [3.6041, 5.32915, 8.40915, 13.51345, 20.67375, 29.2457, 38.5756, 48.2956, 58.22885, 68.28795, 78.4265, 88.61815, 98.84695, 109.1026, 119.37825, 129.6693]

from src.tle import *
parseTLE()

# for showing commentary of the images
import src.comments as comments
comments.parseComments()

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

# formatting log scale lables
def fake_log_fmt(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    b = int(b)
    return r'$1e{{{}}}$'.format(a)

# print("fmt: {}".format(fmt(400000, 2)))

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
                if new_image.got_metadata and new_image.original_pixels > 0:
                    print("image {} does not contain data".format(i))
                    continue

            if require_metadata and not new_image.got_metadata:
                print("image {} does not contain metadata".format(i))
                continue

            if require_metadata and new_image.got_metadata and new_image.time <= obc_time_offset_:
                print("image {} does not have a valid time".format(i))
                continue

            images.append(new_image)

    return images

# load reange of images having a particular type
def loadImageRangeMulti(from_to, image_type, require_data=0, require_metadata=0, outliers=[]):

    images = []

    print("from_to.shape[0]: {}".format(from_to.shape[0]))

    # load images
    for j in range(0, from_to.shape[0]):

      for i in range(from_to[j, 0], from_to[j, 1]):

          try:
              dev_null = outliers.index(i)
              continue
          except:
              pass

          if comments.isNolearn(i):
              print("image {} rejected because of #nolearn".format(i))
              continue

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
        if images[i].type == 32:
            image_dose = np.sum(images[i].data*kevs)/exposure
        elif images[i].type == 1:
            image_dose = np.sum(images[i].data)/exposure

        doses.append(image_dose)

    return np.array(doses)

# calculate the doses in image range
def calculateTotalExposureTime(images):

    total_time = 0

    for i in range(len(images)):

        # calculate the exposure time in seconds
        exposure = images[i].exposure
        if exposure <= 60000:
            exposure = exposure*0.001
        else:
            exposure = 60 + exposure%60000

        total_time += exposure

    return total_time

# calculate the doses in image range
def calculateImageHist(images, bin_size, n_bins, count=False):

    bins = []

    for b in range(n_bins):

        doses = []
        
        low_limit = b*bin_size
        high_limit = (b+1.0)*bin_size

        if b == n_bins - 1:
            high_limit = 150

        for i in range(len(images)):

            image_dose = 0
            empty_image = False

            if images[i].got_data == 0:

               print("Image {} got no data".format(images[i].id))

               empty_image = True

            else:

                temp_image = copy.deepcopy(images[i])

            # calculate the exposure time in seconds
            exposure = images[i].exposure
            if exposure <= 60000:
                exposure = exposure*0.001
            else:
                exposure = 60 + exposure%60000

            if not empty_image:

                nonzero_idcs = np.nonzero(temp_image.data)

                for x, y in zip(nonzero_idcs[0], nonzero_idcs[1]):

                    if temp_image.data[x, y] < low_limit or temp_image.data[x, y] >= high_limit:
                        temp_image.data[x, y] = 0
                    elif count == True:
                        temp_image.data[x, y] = 1

            if empty_image:
                image_dose = 0
            else:
                image_dose = np.sum(temp_image.data)/exposure

            doses.append(image_dose)

        bins.append(np.array(doses))

    return bins

# calculate the doses in image range
def calculateEnergyDose2(images):

    doses = []
    total_exposure_time = 0
    total_pixel_count = 0

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

        total_exposure_time += exposure

        # calculate the doses base on counts
        total_pixel_count += images[i].original_pixels
        image_dose = np.sum(images[i].data*kevs)/exposure

        doses.append(image_dose)

    return np.array(doses), total_exposure_time, total_pixel_count

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
        # image_dose = images[i].original_pixels

        doses.append(image_dose)

    return np.array(doses)

def calculateTotalPixelCount2(images):

    doses = []
    total_exposure_time = 0
    total_pixel_count = 0

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

        total_exposure_time += exposure

        # calculate the doses base on counts
        total_pixel_count += images[i].original_pixels
        image_dose = images[i].original_pixels/exposure

        doses.append(image_dose)

    return np.array(doses), total_exposure_time, total_pixel_count

def createMap(projection, lat=0, lon=0):

    m = []

    if projection == 'ortho':
        m = Basemap(projection=projection, lat_0=lat, lon_0=lon, resolution='l', suppress_ticks=True)
    else:
        m = Basemap(projection=projection, suppress_ticks=True)

    # draw continents
    # m.drawparallels(np.arange(-90, 91, 30))
    # m.drawmeridians(np.arange(-180, 181, 60))
    m.drawcoastlines(linewidth=1.25, zorder=2)
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

def sample_sphere_uniform(n_points):
    x = np.random.normal (0,1,n_points)
    y = np.random.normal(0,1,n_points)
    z = np.random.normal(0,1,n_points)
    pts = np.vstack((x,y,z)).transpose()
    pts = pts/np.repeat(np.atleast_2d(np.linalg.norm(pts,ord=2,axis=1)).transpose(), repeats=3, axis=1)
    lats = np.arcsin(pts[:,-1])*180/3.14
    longs = np.arctan2(pts[:,0], pts[:,1])*180/3.14
    return lats, longs

class Face():
    def __init__(self, init_verts):
        self.vertices = np.zeros((3,3))
        self.vertices = init_verts

    def get_center(self):
        c = np.mean(self.vertices, axis=0)
        return c/np.linalg.norm(c)

    def subdivide_once(self):
        e01 = np.mean(self.vertices[(0,1),:], axis=0)
        e12 = np.mean(self.vertices[(1,2),:], axis=0)
        e20 = np.mean(self.vertices[(0,2),:], axis=0)
        f1 = Face(np.vstack((self.vertices[0,:], e01, e20)))
        f2 = Face(np.vstack((self.vertices[1,:], e01, e12)))
        f3 = Face(np.vstack((self.vertices[2,:], e20, e12)))
        f4 = Face(np.vstack((e01, e12, e20)))
        new_faces = [f1, f2, f3, f4]
        for f in new_faces:
            f.normalize()
        return new_faces

    def normalize(self):
        vertNorm = np.linalg.norm(self.vertices, axis=1)
        vertNorm= np.repeat(np.atleast_2d(vertNorm).transpose(),
                            repeats=3, axis=1)
        self.vertices = self.vertices/vertNorm

##### Geodesic grid generation routines #####
class Sphere():
    def __init__(self, n_subdivs=3):
        v = np.array([[1,1,1],
                      [-1,-1,1],
                      [-1,1,-1],
                      [1,-1,-1]])
        f1 = Face(v[(0,1,2),:]);
        f2 = Face(v[(1,2,3),:]);
        f3 = Face(v[(0,2,3),:]);
        f4 = Face(v[(0,1,3),:]);
        self.faces = [f1,f2,f3,f4]
        v = np.array([[ 1, 0, 0],
                      [ 0, 1, 0],
                      [-1, 0, 0],
                      [ 0,-1, 0],
                      [ 0, 0, 1],
                      [ 0, 0,-1]])
        self.faces = list()
        self.faces.append(Face(v[(0,3,4),:]))
        self.faces.append(Face(v[(0,1,4),:]))
        self.faces.append(Face(v[(1,2,4),:]))
        self.faces.append(Face(v[(2,3,4),:]))
        self.faces.append(Face(v[(0,3,5),:]))
        self.faces.append(Face(v[(0,5,1),:]))
        self.faces.append(Face(v[(5,1,2),:]))
        self.faces.append(Face(v[(5,2,3),:]))

        for f in self.faces:
            f.normalize()

        for i in range(0, n_subdivs):
            self.subdivide()

    def subdivide(self):
        new_faces = list()
        for f in self.faces:
            res = f.subdivide_once()
            new_faces.extend(res)
        self.faces = new_faces

    def get_points(self):
        pts = np.zeros((len(self.faces), 3))
        for i,f in enumerate(self.faces):
            pts[i, :] = f.get_center()
        return pts

    def show(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        pts = self.get_points()
        ax.scatter(pts[:,0], pts[:,1], pts[:,2], marker='.')
        ax.set_xlim([-1,1])
        ax.set_ylim([-1,1])
        ax.set_zlim([-1,1])
        plt.show()

def cart2latlong(pts):
    lats = np.arcsin(pts[:,-1])*180/3.14
    longs = np.arctan2(pts[:,0], pts[:,1])*180/3.14
    return lats, longs
