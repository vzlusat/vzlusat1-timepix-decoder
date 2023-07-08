import datetime
import numpy
import ephem

def parseTLE(file_name = "tle.txt"):

    tle_time = []
    tle1 = []
    tle2 = []

    try:
        print("opening tle file: {}".format(file_name))
        infile = open(file_name, "r")
    except:
        return 0

    i = 0

    # for all lines in the file 
    for line in infile:

        # parse the timestamp
        if i == 0:
            tle_time.append(int(line[0:-1]))

        # parse the first line of tle
        if i == 1:
            tle1.append(line[0:-1])

        # parse the second line of tle
        if i == 2:
            tle2.append(line[0:-1])

        i += 1

        if i == 3:
            i = 0

    return tle1, tle2, tle_time

def findClosestTLE(value, tle1, tle2, tle_time):

    return min(range(len(tle_time)), key=lambda i: numpy.abs(tle_time[i]-value))

def getLatLonAlt(timestamp, tle1, tle2, tle_time):

    closest_tle_idx = findClosestTLE(timestamp, tle1, tle2, tle_time)

    # put the closest tle to the toolboc
    tle = ephem.readtle("0 VZLUSAT", tle1[closest_tle_idx], tle2[closest_tle_idx])

    # find the location at the time
    try:
        tle.compute(datetime.datetime.utcfromtimestamp(timestamp))
    except:
        print("Could not compute tle for timestamp {}".format(timestamp))
        return 0, 0, 0

    # calculate latitude and longitude in degrees
    lon = float(repr(tle.sublong))*(180/3.141592654)
    lat = float(repr(tle.sublat))*(180/3.141592654)
    alt = float(repr(tle.elevation))/1000.0

    return lat, lon, alt, datetime.datetime.utcfromtimestamp(tle_time[closest_tle_idx])
