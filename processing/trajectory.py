#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar
import time
import numpy as np
import calendar

from include.baseMethods import *

from_time = "08.01.2020 10:30:00"
to_time = "09.01.2020 10:30:00"

step_size = 60 # [s]

t_start = int(calendar.timegm(time.strptime(from_time, "%d.%m.%Y %H:%M:%S")))
t_end = int(calendar.timegm(time.strptime(to_time, "%d.%m.%Y %H:%M:%S")))

lats = []
lons = []
times = []

print("Calculating orbit")
i = t_start
state = True
last_change = 0
while i <= t_end:

    latitude, longitude, tle_date = getLatLong(int(i))

    lats.append(latitude)
    lons.append(longitude)
    times.append(i)

    i += step_size

print("Plotting")
def plot_everything(*args):

    fig1 = plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1)

    # #{ map

    m = createMap('cyl')

    # mark the orbit
    for i in range(len(lats)):
        x, y = m(lons[i], lats[i])
        color = 'grey'
        m.scatter(x, y, 10, marker='o', color=color, zorder=5)

    # mark the start
    x, y = m(lons[0], lats[0])
    m.scatter(x, y, 100, marker='o', color='green', zorder=5)

    # mark the end
    x, y = m(lons[-1], lats[-1])
    m.scatter(x, y, 100, marker='o', color='red', zorder=5)

    plt.title('The orbit')

    # #} end of globe south

    plt.show()

pid = os.fork()
if pid == 0:
    plot_everything()
