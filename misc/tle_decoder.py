# pip install pyephem
# sudo apt-get install python-mpltoolkits.basemap

import ephem
import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

tle = ephem.readtle("0 VZLUSAT",
"1 42790U 17036AB  17236.90928386  .00002510  00000-0  11640-3 0  9996",
"2 42790  97.4437 295.9456 0012835  41.8426 318.3788 15.20921507  9461"
)

tle.compute("2017-08-25 21:15:06")
# tle.compute("2017-08-25 21:59:12")
# tle.compute("2017-08-25 19:40:26")
# tle.compute("2017-08-25 21:20:06")

print("lat: {}, long: {}".format(tle.sublong, tle.sublat))

long = float(repr(tle.sublong))*(180/3.141592654)
lat = float(repr(tle.sublat))*(180/3.141592654)

print("{}, {}".format(lat, long))

# set up orthographic map projection with
# perspective of satellite looking down at 50N, 100W.
# use low resolution coastlines.
map = Basemap(projection='ortho',lat_0=lat,lon_0=long,resolution='l')
# draw coastlines, country boundaries, fill continents.
map.drawcoastlines(linewidth=0.25)
map.drawcountries(linewidth=0.25)
map.fillcontinents(color='coral',lake_color='aqua')
# draw the edge of the map projection region (the projection limb)
map.drawmapboundary(fill_color='aqua')
# draw lat/lon grid lines every 30 degrees.
map.drawmeridians(np.arange(0,360,30))
map.drawparallels(np.arange(-90,90,30))

# make up some data on a regular lat/lon grid.
nlats = 1;
lats = lat;
lons = long;
# compute native map projection coordinates of lat/lon grid.
x, y = map(long, lat)
# contour data over the map.

cs = map.scatter(x,y, 80, marker='o', color='k')

plt.title('Location of the measurement')
plt.show()
