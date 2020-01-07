#!/usr/bin/python

import os
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_to = numpy.array([
[36352, 36671], # 1st full res
[36672, 37034], # 2nd full res
[37103, 37862], # 3rd full res
[37863, 38587], # 4rd full res
[38604, 39191], # 5rd full res
[39194, 39958], # 6rd full res
])
outliers=[]

date_range = ''
x_units = '(keV/s)'
x_label = 'Total dose in 14x14x0.3 mm Si'
general_label = 'Radiation dose, 500 km LEO, VZLUSAT-1'
epsilon=0.1

# prepare data
images = loadImageRangeMulti(from_to, 1, 1, 1, outliers)

doses = calculateEnergyDose(images)

lats_orig, lons_orig = extractPositions(images)

#} end of RBF interpolation

def plot_everything(*args):

    print("plotting")

    plt.figure(1)

    ax1 = plt.subplot2grid((1, 1), (0, 0))

    m = createMap('cyl')

    x_m, y_m = m(lons_orig, lats_orig) # project points

    CS = m.hexbin(x_m, y_m, C=numpy.array(doses), gridsize=32, bins="log", cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
    # CS = m.hexbin(x_m, y_m, C=numpy.array(doses), gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    cb.set_label(x_label+' '+x_units)
    plt.title(general_label+', '+date_range, fontsize=13)

    plt.show()

    print("plotting finished")

pid = os.fork()
if pid == 0:
    plot_everything()
