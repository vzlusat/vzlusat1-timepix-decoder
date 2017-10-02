#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import pickle
import matplotlib.patches as mpatches

from src.plotting import *
from src.Results import *

title_text="Raytracing, 150um foils, 150 um spacing, 38 um skew"
file_name="result_new.pkl"

# title_text="Moving Sun, optics retracted, 3rd order reflections"
# file_name="moving_sun_retracted_3rd_refl.pkl"

# title_text="Moving Sun, optics deployed, 3rd order reflections"
# file_name="moving_sun_deployed_3rd_refl.pkl"

# title_text="Moving Sun, optics deployed, 3rd order reflections, optics 1.0 scale"
# file_name="raytrace_80.0_1.0.pkl"

# title_text="Moving Sun, optics deployed, 3rd order reflections, optics 1.5 scale"
# file_name="raytrace_80.0_1.5.pkl"

# title_text="Moving Sun, optics retracted, 3rd order reflections, optics 1.0 scale"
# file_name="raytrace_-50.0_1.0.pkl"

# title_text="Moving Sun, optics retracted, 3rd order reflections, optics 1.5 scale"
# file_name="raytrace_-50.0_1.5.pkl"

# title_text="Moving Sun, optics deployed, 3rd order reflections, optics 1.0 scale"
# file_name="raytrace_deployed_1.0.pkl"

# title_text="Moving Sun, optics deployed, 3rd order reflections, optics 1.5 scale"
# file_name="raytrace_deployed_1.5.pkl"

# title_text="Moving Sun, optics retracted, 3rd order reflections, optics 1.0 scale"
# file_name="raytrace_retracted_1.0.pkl"

# title_text="Moving Sun, optics retracted, 3rd order reflections, optics 1.5 scale"
# file_name="raytrace_retracted_1.5.pkl"

# title_text="Static point source, optics deployed, 3rd order reflections, optics 1.0 scale"
# file_name="point_source_deployed_1.0.pkl"

# title_text="Static point source, optics deployed, 3rd order reflections, optics 1.5 scale"
# file_name="point_source_deployed_1.5.pkl"

print("Loading results")

# ask OS to locate the file
if os.path.isfile(file_name):

    # if the file exists, open it
    with open(file_name, 'rb') as input:
    
        # load the object from the file
        try:
            results = pickle.load(input)
        except:
            print("file \"{}\" is corrupted".format(file_name))

print("Plotting")

optics_segments_buffer = []
timepix_segments_buffer = []
optics_point_buffer = []
timepix_point_buffer = []
source_point_buffer = []
reflected_rays_segment_buffer = []
direct_rays_segment_buffer = []

for i in results.optics_segments_list:
    plotSegment(optics_segments_buffer, i, 'blue', 1)

for i in results.timepix_segments_list:
    plotSegment(timepix_segments_buffer, i, 'green', 1)

for i in results.optics_point_list:
    plotSegment(optics_point_buffer, i, 'red', 10)

for i in results.timepix_point_list:
    plotPoint(timepix_point_buffer, i, 'blue', 20);

for i in results.source_point_list:
    plotPoint(source_point_buffer, i, 'green', 50);

for i in results.direct_rays_segment_list:
    plotSegment(direct_rays_segment_buffer, i, 'yellow', 0.1)

for i in results.reflected_rays_segment_list:
    plotSegment(reflected_rays_segment_buffer, i, 'red', 0.1)

def plot_everything(*args):

    plt.figure(1)
    plt.suptitle(title_text)

    ax = plt.subplot2grid((3, 7), (0, 0), rowspan=2)
    ax.axis([np.min(results.columns), np.max(results.columns), 1, 256])
    ax.plot(results.columns, np.arange(0, 256, 1))

    ax = plt.subplot2grid((3, 7), (0, 1), rowspan=2)
    ax.axis('equal')
# ax.axis([-2, 2, 14/2, 14/2])
    plotSegments(ax, timepix_segments_buffer)
    plotPoints(ax, timepix_point_buffer)

    ax = plt.subplot2grid((3, 7), (0, 2), colspan=6, rowspan=2)

    from scipy.misc import imread
    import matplotlib.cbook as cbook
    # datafile = cbook.get_sample_data('./satellite.jpg')
    img = imread('satellite.jpg')
    x_offs = -11.0
    y_offs = -2.0
    ax.imshow(img, zorder=0, extent=[-210.0+x_offs, 162.0+x_offs, -110.0+y_offs, 83.0+y_offs])

    plotPoints(ax, optics_point_buffer)
    plotPoints(ax, timepix_point_buffer)
    plotSegments(ax, timepix_segments_buffer)
    plotSegments(ax, reflected_rays_segment_buffer)
    plotSegments(ax, direct_rays_segment_buffer)
    plotSegments(ax, optics_segments_buffer)

    optics_legend = mpatches.Patch(color='blue', label='Optics')
    direct_rays_legend = mpatches.Patch(color='yellow', label='Direct rays')
    reflected_rays_legend = mpatches.Patch(color='red', label='Reflected rays')
    timepix_legend = mpatches.Patch(color='green', label='Timepix')
    ax.legend(handles=[optics_legend, direct_rays_legend, reflected_rays_legend, timepix_legend])

    ax.set_xlabel("Distance [mm]")
    ax.set_ylabel("Distance [mm]")

    ax.axis('equal')
    ax.axis([-240, 210, -120, 100])

    ax = plt.subplot2grid((3, 7), (2, 0), colspan=7)
    ax.axis('equal')

    plotPoints(ax, timepix_point_buffer)
    plotPoints(ax, source_point_buffer)
    plotSegments(ax, timepix_segments_buffer)
    plotSegments(ax, reflected_rays_segment_buffer)
    plotSegments(ax, direct_rays_segment_buffer)
    plotSegments(ax, optics_segments_buffer)

    optics_legend = mpatches.Patch(color='blue', label='Optics')
    rays_legend = mpatches.Patch(color='yellow', label='Rays')
    source_legend = mpatches.Patch(color='green', label='Source')
    ax.legend(handles=[optics_legend, rays_legend, source_legend])

    ax.set_xlabel("Distance [mm]")
    ax.set_ylabel("Distance [mm]")

    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.975, top=0.95, wspace=0.3, hspace=0.2)

    plt.show()

# run the plotting in the background
pid = os.fork()
if pid == 0:
    plot_everything()
