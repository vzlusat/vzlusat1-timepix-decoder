#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker
import mpl_toolkits
from mpl_toolkits.basemap import Basemap
import matplotlib.pylab as pl
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
from include.baseMethods import *
import pickle
import math
from timeit import default_timer as timer
import multiprocessing as mp

# set this according to your number of CPU threads... (and subtract one)
n_processes = 12

load_from_cache=True
file_name_cache="cache.pkl"
fps = 30 # []
single_map_duration = 3.0 # [s]
single_rotation_duration = 12.0 # [s]
data_intervals = [
    # [27979, 28095, "2019, duben"], # Combined belt+anomaly scanning 10
    # [35839, 35940, "2019, cervenec"], # Combined belt+anomaly scanning 11
    # [36352, 36671, "title 1# "], 1st full res
    [36672, 37034, "2019, zari"], # 2nd full res
    [37103, 37862, "2019, listopad"], # 3rd full res
    [37863, 38587, "2019, listopad"], # 4th full res
    [38604, 39191, "2019, listopad"], # 5th full res
    [39194, 39961, "2019, prosinec"], # 6th full res
    [39962, 40568, "2020, leden"], # 7th full res
    [40600, 41429, "2020, unor"], # 8th full res
    [41446, 42354, "2020, brezen"], # 9th full res
    [42355, 43038, "2020, brezen"], # 10th full res
    [43072, 43889, "2020, kveten"], # 11th full res
]

# #{ class Cache

class Cache:

    meshgrid_x = []
    meshgrid_y = []
    doses_all = []

    def __init__(self, meshgrid_x, meshgrid_y, doses_all):

        self.meshgrid_x = meshgrid_x
        self.meshgrid_y = meshgrid_y
        self.doses_all = doses_all

# #} end of Cache

my_cm = colormapToTransparent(pl.cm.jet)

pcolor_min = 0
pcolor_max = 7

meshgrid_x = []
meshgrid_y = []
doses_all = []
n_maps = len(data_intervals)

# #{ loadData

def loadData():

    doses_all = []

    meshgrid_y, y_meshgrid = createMeshGrid(150)

    for i in range(0, n_maps):

        from_to = numpy.array([[data_intervals[i][0], data_intervals[i][1]]])

        images = loadImageRangeMulti(from_to, 1, 1, 1, [])

        # doses = calculateTotalPixelCount(images)
        doses = calculateEnergyDose(images)
        doses_log = np.where(doses > 0, np.log10(doses), doses)

        lats_orig, lons_orig = extractPositions(images)

        doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

        rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=5, smooth=1)
        doses_rbf_log = rbf_log(meshgrid_y, y_meshgrid)

        doses_all.append(doses_rbf_log)

    return meshgrid_y, y_meshgrid, doses_all

# #} end of loadData

# #{ LOAD + CACHE + UNCACHE DATA

if load_from_cache:

    # ask OS to locate the file
    if os.path.isfile(file_name_cache):

        # if the file exists, open it
        with open(file_name_cache, 'rb') as input:

            try:
                cache = pickle.load(input)

                meshgrid_x = cache.meshgrid_x
                meshgrid_y = cache.meshgrid_y
                doses_all = cache.doses_all

                print("data loaded from cache")
            except:
                print("file \"{}\" is corrupted".format(file_name_cache))
                exit()

else:
    meshgrid_x, meshgrid_y, doses_all = loadData()

    # save to cache
    cache = Cache(meshgrid_x, meshgrid_y, doses_all)

    with open(file_name_cache, 'wb') as file_cache:

        pickle.dump(cache, file_cache, pickle.HIGHEST_PROTOCOL)
        print("data save to cache")

# #} end of 

# #{ globe animation

# #{ animateGlobe()

def saveGlobe(i):

    fig = plt.figure()

    m = Basemap(projection='ortho', lat_0=0, lon_0=(i*(360.0/(fps*single_rotation_duration)) % 360), resolution='c')
    m.drawcoastlines()

    map_id = int(math.floor((float(i)/float(fps))/float(single_map_duration)))
    # print("frame: {}/{}, map_id: {}".format(i, int(fps*n_maps*single_map_duration), map_id))

    x_m_meshgrid, y_m_meshgrid = m(meshgrid_y, meshgrid_x)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_all[map_id], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="radiacni davka detektoru [$log_{10}$ keV/s]") # draw colorbar

    plt.title(data_intervals[map_id][2], fontsize=13)

    plt.savefig("animation/{0:04d}.png".format(i))

# #} end of animateGlobe()

# #{ genAnimation()

def genAnimationProcess(pidx, from_frame, to_frame):

    n_frames = to_frame - from_frame

    for i in range(from_frame, to_frame):

        saveGlobe(i)

        print("process {}: {}%".format(pidx, int((float(i-from_frame)/float(n_frames))*100.0)))

# #} end of genAnimation()

# #} end of globe animation

n_frames = int(float(fps)*float(n_maps)*single_map_duration)

froms = []
tos = []
for i in range(0, n_processes):

    images_per_cpu = int(float(n_frames)/float(n_processes))

    froms.append(i*images_per_cpu)
    tos.append((i+1)*images_per_cpu)

# initialize the raytracing methods, giving each their own targets to shoot at
processes = [mp.Process(target=genAnimationProcess, args=(x, froms[x], tos[x])) for x in range(n_processes)]

p_idx = 0
for p in processes:
    print("Spawning process {}".format(p_idx))
    p_idx += 1
    p.start()

while True:

    some_alive = 0

    for p in processes:

        if p.is_alive():

            some_alive = 1

    if some_alive == 0:
        break
