#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import pickle
import matplotlib.patches as mpatches

from src.plotting import *
from src.Results import *

title_text="Raytracing"
file_name="results_inside_new.pkl"

# title_text="Moving Sun, Timepix dist 50 mm, reflections: 0"
# file_name="moving_sun_50mm_0refl.pkl"

# title_text="Moving Sun, Timepix dist 5 mm"
# file_name="moving_sun_5mm.pkl"

# title_text="Static Sun, Timepix dist 50 mm"
# file_name="static_sun_0.5deg_50mm.pkl"

# title_text="Static point source, Timepix dist 50 mm"
# file_name="static_sun_point_50mm.pkl"

# title_text="Static point source, Timepix dist 50 mm"
# file_name="static_sun2_point_50mm.pkl"

# title_text="Static point source, Optics deployed, 0 reflections"
# file_name="focus_0_reflections.pkl"

# title_text="Static point source, Optics deployed, 1 reflection"
# file_name="focus_1_reflection.pkl"

# title_text="Static point source, Optics deployed, 2 reflections"
# file_name="focus_2_reflections.pkl"

# title_text="Static point source, Optics deployed, 3 reflections"
# file_name="focus_3_reflections.pkl"

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
    plotSegment(direct_rays_segment_buffer, i, 'yellow', 1)

for i in results.reflected_rays_segment_list:
    plotSegment(reflected_rays_segment_buffer, i, 'red', 1)

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
ax.axis('equal')
ax.axis([-210, 150, -30, 30])

plotPoints(ax, optics_point_buffer)
plotPoints(ax, timepix_point_buffer)
plotSegments(ax, optics_segments_buffer)
plotSegments(ax, timepix_segments_buffer)
plotSegments(ax, reflected_rays_segment_buffer)
plotSegments(ax, direct_rays_segment_buffer)

optics_legend = mpatches.Patch(color='blue', label='Optics')
direct_rays_legend = mpatches.Patch(color='yellow', label='Direct rays')
reflected_rays_legend = mpatches.Patch(color='red', label='Reflected rays')
timepix_legend = mpatches.Patch(color='green', label='Timepix')
ax.legend(handles=[optics_legend, direct_rays_legend, reflected_rays_legend, timepix_legend])

ax.set_xlabel("Distance [mm]")
ax.set_ylabel("Distance [mm]")

ax = plt.subplot2grid((3, 7), (2, 0), colspan=7)
ax.axis('equal')

plotPoints(ax, timepix_point_buffer)
plotPoints(ax, source_point_buffer)
plotSegments(ax, optics_segments_buffer)
plotSegments(ax, timepix_segments_buffer)
plotSegments(ax, reflected_rays_segment_buffer)
plotSegments(ax, direct_rays_segment_buffer)

optics_legend = mpatches.Patch(color='blue', label='Optics')
rays_legend = mpatches.Patch(color='yellow', label='Rays')
source_legend = mpatches.Patch(color='green', label='Source')
ax.legend(handles=[optics_legend, rays_legend, source_legend])

ax.set_xlabel("Distance [mm]")
ax.set_ylabel("Distance [mm]")

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.975, top=0.95, wspace=0.3, hspace=0.2)

plt.show()
