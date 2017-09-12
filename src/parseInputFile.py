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
from src.Image import *
from src.saveImage import *
from src.loadImage import *
from src.baseMethods import getFileName
from src.baseMethods import getPngFileName
import src.statusLine as statusLine
import sys
import os

import datetime

last_time = 0

def parseInputFile(file_path, root):

    try:
        infile = open(file_path, "r")
    except:
        return 0

    files_to_save = {}

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

            temp_image = 0

            if sys.version_info[0] < 3:
                bin_data = [ord(x) for x in data]
                data = bin_data
            else:
                bin_data = [int(x) for x in data]

            if data[0] == ord('A'):

                temp_image = parseMetadata(bin_data[1:], files_to_save)

            elif data[0] == ord('B'):

                temp_image = parseRaw(bin_data[1:], files_to_save)
                
            elif data[0] == ord('D'):

                temp_image = parseBinning8(bin_data[1:], files_to_save)

            elif data[0] == ord('E'):

                temp_image = parseBinning16(bin_data[1:], files_to_save)

            elif data[0] == ord('F'):

                temp_image = parseBinning32(bin_data[1:], files_to_save)

            elif data[0] == ord('h'):

                temp_image = parseRowsSums(bin_data[1:], files_to_save)

            elif data[0] == ord('H'):

                temp_image = parseColsSums(bin_data[1:], files_to_save)

            elif data[0] == ord('e'):

                temp_image = parseEnergyHist(bin_data[1:], files_to_save)

            elif data[0] == ord('Z'):

                parseHouseKeeping(bin_data[1:], last_time)

            elif data[0] == 19:

                if data[1] == 234:

                    parseHouseKeeping(bin_data[3:], last_time)

            else:

                print("UNKNOWN packet")
                print(hex_data)

            if isinstance(temp_image, Image):
                files_to_save[getFileName(temp_image.id, temp_image.type)] = temp_image

    statusLine.set("Saving images to binary files")

    for filename, image in files_to_save.items():

        old_image = loadImage(image.id, image.type)

        if not image.__eq__(old_image):

            print("Image {}_{} was updated".format(image.id, image.type))

            png_filename = getPngFileName(image.id, image.type)

            # delete the png
            try:
                with open(png_filename) as file:
                    os.remove(png_filename)
                    print("Deleting outdated png of {}_{}".format(image.id, image.type))
            except IOError as e:
                pass

        saveImage(image)

    return 1
