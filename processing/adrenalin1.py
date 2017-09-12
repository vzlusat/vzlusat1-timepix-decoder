#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('../')

from include.filtration import *
from src.loadImage import *
from src.Image import *

from mpl_toolkits.axes_grid1 import make_axes_locatable

path = "../images_bin/"

# load the images
images = []
images_filtered = []

images.append(loadImage(401, 1, path))
images.append(loadImage(402, 1, path))
images.append(loadImage(404, 1, path))
images.append(loadImage(807, 1, path))
images.append(loadImage(808, 1, path))
# images.append(loadImage(809, 1, path)) # full of electrons
images.append(loadImage(810, 1, path))
images.append(loadImage(811, 1, path))
images.append(loadImage(812, 1, path))

for i in range(len(images)):

    print("filtering: {}".format(images[i].id))
    images_filtered.append(filterImage(images[i]))

print("Merging images")

merged = numpy.zeros(shape=[256, 256])
merged_filtered = numpy.zeros(shape=[256, 256])

for i in range(len(images)):

    print("merging: {}".format(images[i].id))
    merged = merged + images[i].data
    merged_filtered = merged_filtered + images_filtered[i].data

print("printing merged image")

fig = plt.figure(1)

ax = fig.add_subplot(1, 2, 1)
im = ax.imshow(merged, interpolation='none', cmap='nipy_spectral_r')
ax.set_xlabel("Column (-)", fontsize=25)
ax.set_ylabel("Row (-)", fontsize=25)
ax.set_title("Stacket images, no filtering", fontsize=25)

divider = make_axes_locatable(fig.gca())
cax = divider.append_axes("right", size="5%", pad=0.2)
cbar = fig.colorbar(im, cax)
cbar.ax.set_ylabel('keV', rotation=270, fontsize=12)

ax = fig.add_subplot(1, 2, 2)
im = ax.imshow(merged_filtered, interpolation='none', cmap='nipy_spectral_r')
ax.set_xlabel("Column (-)", fontsize=25)
ax.set_ylabel("Row (-)", fontsize=25)
ax.set_title("Stacket images, individually filtered", fontsize=25)

divider = make_axes_locatable(fig.gca())
cax = divider.append_axes("right", size="5%", pad=0.2)
cbar = fig.colorbar(im, cax)
cbar.ax.set_ylabel('keV', rotation=270, fontsize=12)

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.05)

# create sum

sums = numpy.zeros(shape=[256, 1])

for j in range(0, 255):

    sum = 0

    for i in range(0, 255):

        if merged_filtered[i, j] > 0:

            sum += 1

    sums[j] = sum

fig = plt.figure(2)
ax = fig.add_subplot(1, 1, 1)
x = numpy.linspace(1, 256, 256)
ax.plot(x, sums)

ax.axis([1, 256, numpy.min(sums), numpy.max(sums)])

ax.set_xlabel("Column (-)", fontsize=25)
ax.set_ylabel("Active pixels (-)", fontsize=25)
ax.set_title("Column sum over stacked images", fontsize=25)

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.05)

plt.show()
