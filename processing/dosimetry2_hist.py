#!/usr/bin/python

import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import matplotlib.ticker as ticker # for colorbar

from include.baseMethods import *

from_idx = 417
to_idx = 796

date_range = '30-31.8.2017'
x_units = '[keV/s]'
x_label = 'Total energy'
general_label = 'Measurements in 510 km LEO orbit'

# prepare data
images = loadImageRange(from_idx, to_idx, 32)
doses = calculateEnergyDose(images)
lats_orig, lons_orig = extractPositions(images)

# prepare a transparent colormap
my_cm = colormapToTransparent(pl.cm.jet)

#{ Figure 1

plt.figure(1)

#{ Scatter plot

ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)

m = createMap('cyl')

x_m, y_m = m(lons_orig, lats_orig) # project points

CS = m.hexbin(x_m, y_m, C=numpy.array(doses), bins='log', gridsize=32, cmap=my_cm, mincnt=0, reduce_C_function=np.max, zorder=10)
cb = m.colorbar(location="bottom", label="Z") # draw colorbar

cb.set_label('log10('+x_label+') '+x_units)
plt.title(general_label+', '+date_range, fontsize=13)

#}

#{ Log-scale RBF

ax2 = plt.subplot2grid((2, 2), (1, 0))

doses_log = np.where(doses > 0, np.log(doses), doses)

XX, YY = createMeshGrid(100)

rbf = Rbf(lats_orig, lons_orig, doses_log, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)

m = createMap('cyl')

x_m_meshgrid, y_m_meshgrid = m(YY, XX)

m.pcolor(x_m_meshgrid, y_m_meshgrid, ZZ, cmap=my_cm)

cb = m.colorbar(location="bottom", label="Z") # draw colorbar
cb.set_label('log10('+x_label+') '+x_units)
plt.title('RBF multiquadric (eps=10e-1), log10 scale, '+date_range, fontsize=13)

#}

#{ Lin-scale RBF

ax3 = plt.subplot2grid((2, 2), (1, 1))

rbf = Rbf(lats_orig, lons_orig, doses, function='multiquadric', epsilon=0.1, smooth=0)
ZZ = rbf(XX, YY)
ZZ = np.where(ZZ < 0, 0, ZZ)

m = createMap('cyl')

m.pcolor(x_m_meshgrid, y_m_meshgrid, ZZ, cmap=my_cm)

cb = m.colorbar(location="bottom", label="Z", format=ticker.FuncFormatter(fmt)) # draw colorbar
cb.set_label(x_label+' '+x_units)
plt.title('RBF multiquadric (eps=10e-1), linear scale, '+date_range, fontsize=13)

#}

plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.2)

#} Figure 1

plt.show()
