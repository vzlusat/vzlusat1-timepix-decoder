#!/usr/bin/python

import os
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

my_cm = colormapToTransparent(pl.cm.jet)

pcolor_min = 0
pcolor_max = 7

from_to = numpy.array([[1, 45000]])

# #{ data preparation

def prepare_data():
    global from_to
    outliers=[]
    images = loadImageRangeMulti(from_to, 1, 1, 1, outliers)

    print("images: {}".format(images))

    doses = calculateEnergyDose(images)
    doses_log = np.where(doses > 0, np.log10(doses), doses)

    lats_orig, lons_orig = extractPositions(images)

    doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
    doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

# #{ RBF generation


# create meshgrid for RBF
    x_meshgrid, y_meshgrid = createMeshGrid(150)

# calculate RBF from log data
    rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=1, smooth=1)
    doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
    rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=1, smooth=1)
    doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)


    return x_meshgrid, y_meshgrid, doses_rbf_log


# #} end of RBF generation



# #} end of data preparation

# #{ prepare_time_data

def prepare_time_data(save=True):
    start = 0
    end = 2700
    times = numpy.array([
        [36352, 36671], # 1st full res
        [36672, 37034], # 2nd full res
        [37103, 37862], # 3rd full res
        [37863, 38587], # 4th full res
        [38604, 39191], # 5th full res
        [39194, 39961], # 6th full res
        [39962, 40568], # 7th full res
        [40600, 41429], # 8th full res
        [41446, 42354], # 9th full res
        [42355, 43038], # 10th full res
    ])
    time_x_mesh = np.zeros([10,150,150])
    time_y_mesh = np.zeros([10,150,150])
    time_doses = np.zeros([10,150,150])

    for i in range(times.shape[0]):
        from_to = numpy.array([[times[i,0], times[i,1]]])
        start = end
        end += 2700

        outliers=[]

        pcolor_min = 0
        pcolor_max = 7

        small_plot = 1

        date_range = 'all time'
        x_units = '(keV/s)'
        x_label = 'Total dose in 14x14x0.3 mm Si'
        general_label = 'VZLUSAT-1, 510 km LEO'

# prepare data
        images = loadImageRangeMulti(from_to, 1, 1, 1, outliers)

# print("images: {}".format(images))

        doses = calculateEnergyDose(images)
        doses_log = np.where(doses > 0, np.log10(doses), doses)

        lats_orig, lons_orig = extractPositions(images)

        doses_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses, lats_orig, lons_orig)
        doses_log_wrapped, lats_wrapped, lons_wrapped = wrapAround(doses_log, lats_orig, lons_orig)

#{ RBF interpolation

# create meshgrid for RBF
        x_meshgrid, y_meshgrid = createMeshGrid(150)

# calculate RBF from log data
        rbf_lin = Rbf(lats_wrapped, lons_wrapped, doses_wrapped, function='multiquadric', epsilon=1, smooth=1)
        doses_rbf_lin = rbf_lin(x_meshgrid, y_meshgrid)

# calculate RBF from lin data
        rbf_log = Rbf(lats_wrapped, lons_wrapped, doses_log_wrapped, function='multiquadric', epsilon=1, smooth=1)
        doses_rbf_log = rbf_log(x_meshgrid, y_meshgrid)

        time_x_mesh[i] = x_meshgrid
        time_y_mesh[i] = y_meshgrid
        time_doses[i] = doses_rbf_log

    return time_x_mesh, time_y_mesh, time_doses

# #} end of prepare_time_data

# #{ generate globe

def gen_globe(x_mesh, y_mesh, doses):
    fig = plt.figure()
    m = createMap('ortho', -90, 0)
    x_m_meshgrid, y_m_meshgrid = m(y_mesh, x_mesh)
    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar

    plt.title('Radiation dose in (keV/s)', fontsize=13)
    plt.show()


# #} end of generate globe

# #{ generate animated globe without time change


def init_animation():
    m = createMap('ortho', 0, 40)
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    return m
def animate(i):
    plt.clf()
    m = createMap('ortho', 0, i+10)
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)

    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    plt.title('Radiation dose in (keV/s)', fontsize=13)
#     mpl_toolkits.basemap.shiftgrid(i, )
    return m

# n_frames - number of globe rotation ( 1 rotation is 1 degree of the globe )
# time_between_frames - delay between frames
# save = True - is a bool variable that checks if to save the animation to a gif or not 
# plot = True - is a bool variable that checks if to plot the result of animation
def gen_globe_animated(n_frames, frame_delay, save=True, plot=True):
    plt.style.use('seaborn-pastel')

    fig = plt.figure()
    m = createMap('ortho', 0, 40)
    x_m_meshgrid, y_m_meshgrid = m(y_meshgrid, x_meshgrid)
    m.pcolor(x_m_meshgrid, y_m_meshgrid, doses_rbf_log, cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, ', fontsize=13)
    anim = FuncAnimation(fig, animate, init_func=init_animation,
                                   frames=frame_delay, interval=speed)
    # print(anim.to_html5_video())
    if save:
        anim.save('globe_animated.gif', writer='imagemagick')
    if plot:
        plt.show()
# result is in globe.gif - it is compiling 5-10 minutes though



# #} end of generate animated globe without time change

# #{ flat map animation generator

def init_animation_time():
   
    m = createMap('cyl')
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[0], time_x_mesh[0])

    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[0], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    return m
def animate_time(i):
    plt.clf()
    m = createMap('cyl')
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[i], time_x_mesh[i])

    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[i], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    plt.title('Radiation dose, 500 km LEO (in keV/s)', fontsize=13)
#     mpl_toolkits.basemap.shiftgrid(i, )
    return m


# save = True - is a bool variable that checks if to save the animation to a gif or not 
# plot = True - is a bool variable that checks if to plot the result of animation
def gen_flatmap_animation_with_time(save=True, plot=True):

    fig = plt.figure()
    m = createMap('cyl')
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[0], time_x_mesh[0])
    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[0], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, ', fontsize=13)

    anim = FuncAnimation(fig, animate_time, init_func=init_animation_time,
                                   frames=4, interval=300)
    if save:
        anim.save('flat_time.gif', writer='imagemagick')
    if plot:
        plt.show()



# #} end of flat map animation generator 

# #{ globe animation with time

# time is a variable to calculate which timeFrame to load in the animate_glob_time function, that creates the next frame
# the solution is not very elegant, I am kinda sure that you can somehow pass the arguments, but I din't do the research
# TODO: pass variables through args to the animate function
time = 0

def init_globe():
   
    m = createMap('ortho', 0, 40)
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[0], time_x_mesh[0])

    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[0], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

 
    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    return m
def animate_glob_time(i):
    plt.clf()
    global time
    m = createMap('ortho', 0, i+10)
    # this selects a frame, number 4 is number of different timeframes at all, since we have only 4 defined in the generation function 
    # again, not very elegant
    # TODO: change to dynamic
    t = time//4
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[t], time_x_mesh[t])
    
    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[t], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)

    cb = m.colorbar(location="bottom", label="Z") # draw colorbar
    plt.title('Radiation dose, 500 km LEO (in keV/s)', fontsize=13)
#     mpl_toolkits.basemap.shiftgrid(i, )
    
    time+=1
    if time==16:
        time=0
    return m


# @param:
# n_frames - number of globe rotation ( 1 rotation is 1 degree of the globe )
# time_between_frames - delay between frames
# save = True - is a bool variable that checks if to save the animation to a gif or not 
# plot = True - is a bool variable that checks if to plot the result of animation
def gen_globe_animated_with_time(n_frames,time_between_frames, save=True, plot=True):
    fig = plt.figure()
    m = createMap('ortho', 0, 40)
    x_m_meshgrid, y_m_meshgrid = m(time_y_mesh[0], time_x_mesh[0])
    m.pcolor(x_m_meshgrid, y_m_meshgrid, time_doses[0], cmap=my_cm, vmin=pcolor_min, vmax=pcolor_max)
    plt.title('RBF multiquadric (eps=10e-1), linear scale, ', fontsize=13)


    anim = FuncAnimation(fig, animate_glob_time, init_func=init_globe,
                         frames=20, interval=1)
    if save:
        anim.save('globe_time.gif', writer='imagemagick')
    if plot:
        plt.show()


# #} end of globe animation with time

# Without time
# x_meshgrid, y_meshgrid, doses_rbf_log = prepare_data()
# gen_globe_animated(25, 0.1)
# Animation with time
time_x_mesh, time_y_mesh, time_doses = prepare_time_data()
# gen_flatmap_animation_with_time()
gen_globe_animated_with_time(2, 0.01, save=False)
