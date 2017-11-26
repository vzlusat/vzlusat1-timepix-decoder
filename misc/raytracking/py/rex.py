#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import pickle
import time

from src.geometry import *
from src.plotting import *
from src.Results import *

t = time.time()

optics_segments_list = []
timepix_segments_list = []
optics_point_list = []
timepix_point_list = []
source_point_list = []
reflected_rays_segment_list = []
direct_rays_segment_list = []

foil_spacing = 1.105
foil_thickness = 0.300
foil_length = 150.0
timepix_x = 0.0 # here is the sensos in reality
n_foils = 46
optics_skew = 0.063
# optics_skew = 0.0
optics_y_offset = (-n_foils/2.0)*optics_skew
optics_y = -(foil_spacing)*n_foils*0.5
timepix_size = 14.0
optics_x = 1425.0 - foil_length# deployed
# optics_x = 1681.0 - foil_length# deployed

#{ Create Optics

foils = []

for i in range(n_foils):

    # bottom points
    p1 = Point(optics_x,  optics_y + i*foil_spacing - foil_thickness/2.0)
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
        ptemp = Point(p2.coordinates[0], -50)
        stemp = Segment(p2, ptemp)
        foils.append(stemp)

        ptemp2 = Point(0, -50)
        stemp = Segment(ptemp, ptemp2)
        foils.append(stemp)

    if i == n_foils-1:
        ptemp = Point(p4.coordinates[0], 50)
        stemp = Segment(p4, ptemp)
        foils.append(stemp)

        ptemp2 = Point(0, 50)
        stemp = Segment(ptemp, ptemp2)
        foils.append(stemp)

    noise = np.random.normal(0, 0.009)
    if noise >  0.003:
        noise = 0.003
    elif noise < -0.003:
        noise = -0.003
    noise = 0
    print("noise: {}".format(noise))
    optics_y_offset += optics_skew + noise

# foils.append(Segment(Point(27, -50), Point(-200, -50)))
# foils.append(Segment(Point(27, 50), Point(-200, 50)))
# foils.append(Segment(Point(-200, 50), Point(-200, -50)))
# foils.append(Segment(Point(27, 50), Point(27, 25)))
# foils.append(Segment(Point(27, -50), Point(27, -25)))
# foils.append(Segment(Point(-30, -50), Point(-30, -15)))

#} end of Create Optics

#{ Create the sensor

p1 = Point(timepix_x, -timepix_size/2.0)
p2 = Point(timepix_x, +timepix_size/2.0)
timepix_segment = Segment(p1, p2)
timepix_segments_list.append(timepix_segment)

#} end of Create the sensor

# simulate

# Sun 3362
source_x = 1000*1000*149.6e6

# Lab source distance
# source_x = 3362

# aparent point size
# source_x = 1425.0 + 50000.0

n_processes = 11

# moving source
# source_min_y = -0.5
# source_max_y = 0.5
# source_step = 0.2

# static point source
source_min_y = 0.0
source_max_y = 0.0
source_step = 1

# static source, 0.5deg
# source_min_y = np.sin(deg2rad(-0.2))*source_x
# source_max_y = np.sin(deg2rad(0.2))*source_x
# source_step = np.sin(deg2rad(0.04))*source_x

# static source, 0.1deg
# source_min_y = np.sin(deg2rad(-0.05))*source_x
# source_max_y = np.sin(deg2rad(0.05))*source_x
# source_step = np.sin(deg2rad(0.01))*source_x

target_max_y = 16.0
target_min_y = -16.0

# target_max_y = 8.0
# target_min_y = -8.0

target_step = 0.01 # moving target, 8 min run
# target_step = 0.0025 # for point sources
# target_step = 0.05 # for quick testing
# target_step = 0.05 # for quick testing

target_x = timepix_x-20.0

max_reflections = 3
critical_angle = deg2rad(0.5)

columns = np.zeros(shape=[256])

class Ray:

    def __init__(self, timepix_point, ray):

        self.timepix_point = timepix_point
        self.ray = ray

direct_rays_queue = mp.Queue() 
reflected_ray_queue = mp.Queue() 

stdout_lock = mp.Lock()
queue_lock = mp.Lock()

#{ Raytracing process

def do_raytracing(pidx, source_ys, source_x, target_ys, target_x, foils, timepix_segment, direct_rays_queue, reflected_ray_queue, stdout_lock, queue_lock, max_reflections, critical_angle):

    import sys

    # source_ys = np.arange(y_min, y_max, step)

    foils.append(timepix_segment)

    max_iter = max_reflections + 1

    n_sources = len(source_ys)
    n_targets = len(target_ys)
    cur_source = 0

    last_print = time.time()
    time_start = time.time()

    for source_y in source_ys:

        cur_source += 1
        cur_target = 0

        for target_y in target_ys:

            cur_target += 1

            if time.time() - last_print >= 1.0:
                stdout_lock.acquire()
                elapsed = time.time() - time_start
                left = (elapsed/(float(cur_source-1)+float(cur_target)/float(n_targets)))*n_sources - elapsed
                print("worker {}: source {}/{}, target {}/{}, time left: {}min {}s".format(pidx, cur_source, n_sources, cur_target, n_targets, math.floor(left/60), math.floor(left%60)))
                stdout_lock.release()
                last_print = time.time()

            source = Point(source_x, source_y)
            timepix_point = Point(target_x, target_y)
            ray = Segment(source, timepix_point)
            timepix_hit = 0

            reflected_rays = []
            final_ray = []
            prev_segment = []

            for i in range(max_iter):

                dist_min = sys.float_info.max
                point_min = 0
                incident_segment = []

                #{ find collisions with all foils

                for seg in foils:

                    if not seg.__eq__(prev_segment):

                        intersection = segmentsIntersection(seg, ray)

                        if isinstance(intersection, Point):

                            dist = pointDistance(intersection, ray.x)

                            if dist < dist_min:
                                dist_min = dist
                                point_min = intersection
                                incident_segment = seg

                #} end of find collisions with all foils

                if isinstance(point_min, Point):

                    # print("point_min.coordinates: {}".format(point_min.coordinates))

                    the_ray = Segment(ray.x, point_min)

                    if incident_segment.__eq__(timepix_segment):

                        # print("timepix collision")

                        timepix_hit = 1
                        final_ray = the_ray
                        # i = max_iter+1
                        break

                    else:

                        # print("segment collision")

                        # create a normal segment to the incident segment in the incident point
                        normal_segment = perpendicularSegment(incident_segment, point_min, 1.0)

                        reflected_source = reflectPointOverLine(normal_segment.line, ray.x)

                        angle = (math.pi-abs(angleVectors(point_min, ray.x, reflected_source)))/2.0

                        if abs(angle) > critical_angle:

                            # i = max_iter+1
                            # print("over critical_angle")
                            break

                        else:

                            # stratch the new ray out
                            segment_vector = reflected_source.coordinates - point_min.coordinates
                            reflected_source.coordinates += 10*segment_vector

                            # plotSegment(segment_buffer, ray_plot, 'green', 1)
                            reflected_rays.append(the_ray)

                            ray = Segment(point_min, reflected_source)
                            ray_vec = normalizeLine(ray.y.coordinates - ray.x.coordinates)
                            ray.x.coordinates[0] += ray_vec[0]*0.0001
                            ray.x.coordinates[1] += ray_vec[1]*0.0001
                            # print("reflecting ray")

                    prev_segment = incident_segment

                else:
                    # i = max_iter+1
                    break

            if timepix_hit == 1:

                #{ Register the hit

                col_point = segmentsIntersection(timepix_segment, ray)
                ray_segment = Segment(timepix_point, source)

                # empty the reflected rays queue
                if len(reflected_rays) > 0:
                    for ray in reflected_rays:
                        queue_lock.acquire()
                        my_output = Ray(0, ray)
                        while reflected_ray_queue.full():
                            print("pidx: {} Queue full".format(pidx))
                        reflected_ray_queue.put(my_output)
                        queue_lock.release()

                    my_output = Ray(final_ray.y, final_ray)
                    while reflected_ray_queue.full():
                        print("pidx: {} Queue full".format(pidx))
                    reflected_ray_queue.put(my_output)
                else:
                    # and add the final ray to the timepix
                    queue_lock.acquire()
                    my_output = Ray(final_ray.y, final_ray)
                    while direct_rays_queue.full():
                        print("pidx: {} Queue full".format(pidx))
                    direct_rays_queue.put(my_output)
                    queue_lock.release()

                #} end of Register the hit

    stdout_lock.acquire()
    print("Process {} has finished".format(pidx))
    stdout_lock.release()

#} end of Raytracing process

target_ys = []
for i in range(n_processes):
    target_min = target_min_y + i*(target_max_y-target_min_y)/n_processes
    target_max = target_min_y + (i+1)*(target_max_y-target_min_y)/n_processes - target_step
    target_ys.append(np.arange(target_min, target_max, target_step))

source_ys = []
i = source_min_y
while i <= source_max_y:
   
    source_ys.append(i)
    i += source_step

print("source_ys: {}".format(source_ys))

processes = [mp.Process(target=do_raytracing, args=(x, source_ys, source_x, target_ys[x], target_x, foils, timepix_segment, direct_rays_queue, reflected_ray_queue, stdout_lock, queue_lock, max_reflections, critical_angle)) for x in range(n_processes)]

p_idx = 0
for p in processes:
    print("Spawning process {} with min={}, max={}, step={}".format(p_idx, target_ys[p_idx][0], target_ys[p_idx][-1], target_step))
    p_idx += 1
    p.start()

while True:

    some_alive = 0

    for p in processes:

        if p.is_alive():

            some_alive = 1

            queue_lock.acquire()

            if not direct_rays_queue.empty():

                result = direct_rays_queue.get_nowait()

                if isinstance(result.timepix_point, Point):

                    timepix_point_list.append(result.timepix_point)
                    pixel = np.floor((result.timepix_point.coordinates[1]+timepix_size/2.0) / (timepix_size/255.0) + 1.0)
                    if pixel >= 0 and pixel <= 255:
                        columns[int(pixel)] += 1

                direct_rays_segment_list.append(result.ray)

            if not reflected_ray_queue.empty():

                result = reflected_ray_queue.get_nowait()

                if isinstance(result.timepix_point, Point):

                    timepix_point_list.append(result.timepix_point)
                    pixel = np.floor((result.timepix_point.coordinates[1]+timepix_size/2.0) / (timepix_size/255.0) + 1.0)
                    if pixel >= 0 and pixel <= 255:
                        columns[int(pixel)] += 1

                reflected_rays_segment_list.append(result.ray)

            queue_lock.release()

    if some_alive == 0:
        break

for i in foils:
    optics_segments_list.append(i)

elapsed = time.time() - t
print("elapsed: {}".format(elapsed))

# try to open the file
print("Saving results")
# file_name="raytracing_{}_{}.pkl".format("deployed" if optics_deployed else "retracted", scaling_factor)
file_name="result_new.pkl"
results = Results(optics_segments_list, timepix_segments_list, optics_point_list, timepix_point_list, source_point_list, reflected_rays_segment_list, direct_rays_segment_list, columns)
with open(file_name, 'wb') as direct_rays_queue:

    try:
       pickle.dump(results, direct_rays_queue, pickle.HIGHEST_PROTOCOL)
    except:
        print("file \"{}\" could not be saved".format(file_name))

import plot_rex
