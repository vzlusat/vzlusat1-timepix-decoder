#!/usr/bin/python

import sys
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('../')

from include.filtration import *
from src.loadImage import *
from src.Image import *

path = "../images_bin/"

# load the images
images = []
images_filtered = []

images.append(loadImage(401, 1, path))
images.append(loadImage(402, 1, path))
images.append(loadImage(404, 1, path))

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

plt.figure(1)
plt.subplot(1, 2, 1)
plt.imshow(merged, interpolation='none', cmap='nipy_spectral_r')
plt.subplot(1, 2, 2)
plt.imshow(merged_filtered, interpolation='none', cmap='nipy_spectral_r')
plt.show()
