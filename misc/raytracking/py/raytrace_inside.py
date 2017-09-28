#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import pickle
import time

from src.lineIntersection import *
from src.Segment import Segment
from src.Point import Point
from src.Line import Line
from src.segmentLineIntersection import *
from src.Results import *

t = time.time()

optics_segments_list = []
timepix_segments_list = []
optics_point_list = []
timepix_point_list = []
source_point_list = []
rays_segment_list = []

foil_spacing = 0.300
foil_thickness = 0.150
foil_length = 60.0
optics_x = -foil_length
timepix_x = -110.0
# timepix_x = -65.0
n_foils = 55
optics_skew = 0.038
optics_y_offset = (-n_foils/2.0)*optics_skew
optics_y = -(foil_spacing)*n_foils*0.5
timepix_size = 14.0

#{ Create Optics

foils = []

for i in range(n_foils):

    # bottom points
    p1 = Point(optics_x, optics_y + i*foil_spacing - foil_thickness/2.0)
    p2 = Point(optics_x + foil_length, optics_y + i*foil_spacing+optics_y_offset - foil_thickness/2.0)

    # top points
    p3 = Point(optics_x, optics_y + i*foil_spacing + foil_thickness/2.0)
    p4 = Point(optics_x + foil_length, optics_y + i*foil_spacing+optics_y_offset + foil_thickness/2.0)

    s1 = Segment(p1, p2) 
    s2 = Segment(p3, p4)
    s3 = Segment(p1, p3)
    s4 = Segment(p2, p4)

    foils.append(s3)
    foils.append(s1)
    foils.append(s2)
    foils.append(s4)

    if i == 0:
        ptemp = Point(0, -50)
        stemp = Segment(p2, ptemp)
        foils.append(stemp)

    if i == n_foils-1:
        ptemp = Point(0, 50)
        stemp = Segment(p4, ptemp)
        foils.append(stemp)

    optics_y_offset += optics_skew

foils.append(Segment(Point(0, -50), Point(-200, -50)))
foils.append(Segment(Point(0, 50), Point(-200, 50)))

#} end of Create Optics

#{ Create the sensor

p1 = Point(timepix_x, -timepix_size/2.0)
p2 = Point(timepix_x, +timepix_size/2.0)
timepix_segment = Segment(p1, p2)
timepix_segments_list.append(timepix_segment)

#} end of Create the sensor

# simulate

# Sun distance
source_x = 1000*1000*149.6e6

# Lab source distance
# source_x = 3000

def deg2rad(deg):
    
    return (np.pi/180)*deg

n_processes = 8

# moving source
# source_min_y = -np.sin(deg2rad(1.5))*source_x
# source_max_y = np.sin(deg2rad(1.5))*source_x
# source_step = np.sin(deg2rad(0.02))*source_x

# static source
source_min_y = np.sin(deg2rad(0.51))*source_x
source_max_y = np.sin(deg2rad(0.53))*source_x
# source_step = np.sin(deg2rad(0.02))*source_x
source_step = (source_max_y - source_min_y)/(n_processes*2)

timepix_step = 0.01
# source_ys = [0]
timepix_ys = np.arange(-timepix_size/2, +timepix_size/2, timepix_step)

reflections=True

columns = np.zeros(shape=[256])

for i in np.arange(source_min_y, source_max_y, source_step):
    source_point_list.append(Point(source_x, i))

class Output:

    def __init__(self, timepix_point, ray):

        self.timepix_point = timepix_point
        self.ray = ray

output = mp.Queue() 

stdout_lock = mp.Lock()
queue_lock = mp.Lock()

def do_raytracing(pidx, y_min, y_max, step, timepix_ys, timepix_x, foils, timepix_segment, output, stdout_lock, queue_lock):

    source_ys = np.arange(y_min, y_max, step)

    my_timepix_points = []
    my_rays = []

    for source_y in source_ys:

        stdout_lock.acquire()
        print("{}: source_y: {}".format(pidx, source_y))
        stdout_lock.release()

        for timepix_y in timepix_ys:

            source = Point(source_x, source_y)
            timepix_point = Point(timepix_x, timepix_y)
            ray = Line(source, timepix_point)

            collision = 0
            for foil in foils:

                col_point = segmentLineIntersection(foil, ray)

                if isinstance(col_point, Point): # we got a collision
                    
                    collision = 1
                    break

            if collision == 0:

                col_point = segmentLineIntersection(timepix_segment, ray)
                ray_segment = Segment(timepix_point, source)

                queue_lock.acquire()
                my_output = Output(col_point, ray_segment)
                while output.full():
                    print("pidx: {} Queue full".format(pidx))
                output.put(my_output)
                queue_lock.release()

    stdout_lock.acquire()
    print("Process {} has finished".format(pidx))
    stdout_lock.release()

mins = []
maxs = []
for i in range(n_processes):
    mins.append(source_min_y + i*(source_max_y-source_min_y)/n_processes)
    maxs.append(source_min_y + (i+1)*(source_max_y-source_min_y)/n_processes - source_step)

processes = [mp.Process(target=do_raytracing, args=(x, mins[x], maxs[x], source_step, timepix_ys, timepix_x, foils, timepix_segment, output, stdout_lock, queue_lock)) for x in range(n_processes)]

p_idx = 0
for p in processes:
    print("Spawning process {} with min={}, max={}, step={}".format(p_idx, mins[p_idx], maxs[p_idx], source_step))
    p_idx += 1
    p.start()

while True:

    some_alive = 0

    for p in processes:

        if p.is_alive():

            some_alive = 1
        
            queue_lock.acquire()
            if not output.empty():
                result = output.get_nowait()
            else:
                queue_lock.release()
                continue
            queue_lock.release()

            if isinstance(result.timepix_point, Point):

                timepix_point_list.append(result.timepix_point)
                pixel = np.floor((result.timepix_point.coordinates[1]+timepix_size/2.0) / (timepix_size/255.0) + 1.0)
                if pixel >= 0 and pixel <= 255:
                    columns[int(pixel)] += 1

                rays_segment_list.append(result.ray)

    if some_alive == 0:
        break

for i in foils:
    optics_segments_list.append(i)

elapsed = time.time() - t
print("elapsed: {}".format(elapsed))

# try to open the file
print("Saving results")
file_name="results_inside_new.pkl"
results = Results(optics_segments_list, timepix_segments_list, optics_point_list, timepix_point_list, source_point_list, rays_segment_list, columns)
with open(file_name, 'wb') as output:

    try:
       pickle.dump(results, output, pickle.HIGHEST_PROTOCOL)
    except:
        print("file \"{}\" could not be saved".format(file_name))

import plot
