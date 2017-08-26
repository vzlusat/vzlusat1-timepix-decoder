import datetime
import numpy
import ephem

tle_time = []
tle1 = []
tle2 = []

def parseTLE():

    try:
        infile = open("tle.txt", "r")
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

def findClosestTLE(value):

    return min(range(len(tle_time)), key=lambda i: numpy.abs(tle_time[i]-value))

def getLatLong(timestamp):

    closest_tle_idx = findClosestTLE(timestamp)

    # put the closest tle to the toolboc
    tle = ephem.readtle("0 VZLUSAT", tle1[closest_tle_idx], tle2[closest_tle_idx])

    # find the location at the time
    tle.compute(datetime.datetime.utcfromtimestamp(timestamp))

    # calculate latitude and longitude in degrees
    lon = float(repr(tle.sublong))*(180/3.141592654)
    lat = float(repr(tle.sublat))*(180/3.141592654)

    return lat, lon, datetime.datetime.utcfromtimestamp(tle_time[closest_tle_idx])
