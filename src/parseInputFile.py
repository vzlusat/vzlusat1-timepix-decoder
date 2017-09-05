import binascii
from src.parseMethods import parseMetadata
from src.parseMethods import parseBinning8
from src.parseMethods import parseBinning16
from src.parseMethods import parseBinning32
from src.parseMethods import parseColsSums
from src.parseMethods import parseRowsSums
from src.parseMethods import parseEnergyHist
from src.parseMethods import parseRaw
from src.parseMethods import parseHouseKeeping

import datetime

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

last_time = 0

def parseInputFile(file_path, v, root, autogenerate_csv):

    try:
        infile = open(file_path, "r")
    except:
        return 0

    # for all lines in the file 
    for line in infile:

        # if the line contains word "time"
        if line.find("time") > -1:

            try:
                last_time = int(line[7:16])+946684800
            except:
                last_time = 0

        # if the line contains word "data"
        if line.find("data") > -1:

            # select the part with the data
            if sys.getsizeof(line) % 2 == 1:
                hex_data = line[7:-1]
            else:
                hex_data = line[7:-2]

            # convert to binary
            try:
                data = binascii.unhexlify(hex_data)
            except:
                 print("Unhexification failed on data: {}".format(hex_data))
                 continue

            if sys.version_info[0] < 3:
                bin_data = [ord(x) for x in data]
                data = bin_data
            else:
                bin_data = [int(x) for x in data]

            if data[0] == ord('A'):

                v.set("Parsing metadata")
                root.update()
                parseMetadata(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('B'):

                v.set("Parsing image (raw)")
                root.update()
                parseRaw(bin_data[1:], autogenerate_csv)
                
            elif data[0] == ord('D'):

                v.set("Parsing image (binning-8)")
                root.update()
                parseBinning8(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('E'):

                v.set("Parsing image (binning-16)")
                root.update()
                parseBinning16(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('F'):

                v.set("Parsing image (binning-32)")
                root.update()
                parseBinning32(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('h'):

                v.set("Parsing image (rows summ)")
                root.update()
                parseRowsSums(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('H'):

                v.set("Parsing image (cols summ)")
                root.update()
                parseColsSums(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('e'):

                v.set("Parsing image (energy hist.)")
                root.update()
                parseEnergyHist(bin_data[1:], autogenerate_csv)

            elif data[0] == ord('Z'):

                v.set("Parsing house keeping")
                root.update()
                parseHouseKeeping(bin_data[1:], last_time, autogenerate_csv)

            elif data[0] == 19:

                if data[1] == 234:

                    v.set("Parsing HKC house keeping")
                    root.update()
                    parseHouseKeeping(bin_data[3:], last_time, autogenerate_csv)

            else:

                print("UNKNOWN packet")
                print(hex_data)

    return 1
