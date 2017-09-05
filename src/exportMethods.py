import numpy
import math
from src.Image import Image 
from src.baseMethods import getExportDataName
from src.baseMethods import getExportMetadataName
from src.baseMethods import getExportHkName
import datetime
import csv
from src.tle import *
import src.settings as settings
from src.HouseKeeping import *

def exportHouseKeeping(data):

    hk_array = [None] * 16;

    with open(getExportHkName(data.images_taken, data.time_since_boot, data.boot_count), "w") as hk_file:

        hk_array[0] = str(data.boot_count)
        hk_array[1] = str(data.images_taken)
        hk_array[2] = str(data.temperature)
        hk_array[3] = str(data.fram_status)
        hk_array[4] = str(data.medipix_status)
        hk_array[5] = str(data.time_since_boot)
        hk_array[6] = str(data.TIR_max)
        hk_array[7] = str(data.TIR_min)
        hk_array[8] = str(data.IR_max)
        hk_array[9] = str(data.IR_min)
        hk_array[10] = str(data.UV1_max)
        hk_array[11] = str(data.UV1_min)
        hk_array[12] = str(data.UV2_max)
        hk_array[13] = str(data.UV2_min)
        hk_array[14] = str(data.temp_max)
        hk_array[15] = str(data.temp_min)

        for i in range(0, 16):

            hk_file.write(data.housekeeping_labels[i]+" "+hk_array[i])

            if i < 16:

                hk_file.write("\n")

        if settings.use_globus:
            latitude, longitude, tle_date = getLatLong(data.time)
            hk_file.write("lat, long, tle_time: {}, {}, {}".format(latitude, longitude, tle_date))


def exportMetadata(image):

    if image.got_metadata == 0:
        return

    metadatas_array = [None] * 21;

    with open(getExportMetadataName(image.id, image.type), "w") as metadata_file:

        metadatas_array[0] = str(image.id)

        if image.type == 1:
            img_type = "Full resolution"
        elif image.type == 2:
            img_type = "Binning 8"
        elif image.type == 4:
            img_type = "Binning 16"
        elif image.type == 8:
            img_type = "Binning 32"
        elif image.type == 16:
            img_type = "Column and row sums"
        elif image.type == 32:
            img_type = "Histogram"

        metadatas_array[1] = str(img_type)

        if image.mode == 0:
            mode = "MPX (Counting)"
        else:
            mode = "TOT (Energy)"

        metadatas_array[2] = str(mode)
        metadatas_array[3] = str(image.threshold)
        metadatas_array[4] = str(image.bias)

        exposure = image.exposure

        if image.exposure <= 60000:
            exposure = image.exposure*0.001
        else:
            exposure = 60 + image.exposure%60000

        metadatas_array[5] = "{0:3.3f}".format(exposure)

        metadatas_array[6] = str(image.filtering)
        metadatas_array[7] = str(image.filtered_pixels)
        metadatas_array[8] = str(image.original_pixels)
        metadatas_array[9] = str(image.min_original)
        metadatas_array[10] = str(image.max_original)
        metadatas_array[11] = str(image.min_filtered)
        metadatas_array[12] = str(image.max_filtered)
        metadatas_array[13] = str(image.temperature)
        metadatas_array[14] = str(image.temp_limit)
        metadatas_array[15] = str(image.pxl_limit)
        metadatas_array[16] = str(image.uv1_thr)

        attitude = ""
        for att in image.attitude:
            attitude += str(att)+" "

        metadatas_array[17] = str(attitude)

        position = ""
        for pos in image.position:
            position += str(pos)+" "

        metadatas_array[18] = str(position)

        metadatas_array[19] = str(image.time)

        if image.type == 2:
            chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+15)
        elif image.type == 4:
            chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+3)
        elif image.type == 8:
            chunk_id = str(image.chunk_id)
        elif image.type == 16:
            chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+7)
        elif image.type == 32:
            chunk_id = str(image.chunk_id)
        elif image.type == 1:
            chunk_id = str(image.chunk_id)+" to "+str(image.chunk_id+int(numpy.floor(image.filtered_pixels/20)))

        metadatas_array[20] = str(chunk_id)

        for i in range(0, 21):

            metadata_file.write(image.metadata_labels[i]+" "+metadatas_array[i])
            metadata_file.write("\n")

        if settings.use_globus:
            latitude, longitude, tle_date = getLatLong(image.time)
            metadata_file.write("lat, long, tle_time: {}, {}, {}\n".format(latitude, longitude, tle_date))

        if image.type == 32:
            metadata_file.write("Histogram bins [bin1_min, bin1_max=bin2_min, ..., bind16_max], the last bin contains also all higher energies.\n")
            metadata_file.write("[2.9807, 4.2275, 6.4308, 10.3875, 16.6394, 24.7081, 33.7833, 43.3679, 53.2233, 63.2344, 73.3415, 83.5115, 93.7248, 103.9691, 114.2361, 124.5204, 134.8182]\n")

def exportBinning(image):

    if image.got_data == 1:
        if image.type == 2:
            size = 32
        elif image.type == 4:
            size = 16
        elif image.type == 8:
            size = 8
        
        with open(getExportDataName(image.id, image.type), "w") as data_file:

            writer = csv.writer(data_file, quoting=csv.QUOTE_NONE)
        
            for i in range(0, size):
                writer.writerow(['{0:d}'.format(math.trunc(x)) for x in image.data[i, :]])

    exportMetadata(image)

def exportSums(image):

    if image.got_data == 1:
        with open(getExportDataName(image.id, image.type), "w") as data_file:

            writer = csv.writer(data_file, quoting=csv.QUOTE_NONE)
        
            writer.writerow(['{0:d}'.format(math.trunc(x)) for x in image.data[0, :]])
            writer.writerow(['{0:d}'.format(math.trunc(x)) for x in image.data[1, :]])

    exportMetadata(image)

def exportHistogram(image):

    if image.got_data == 1:
        with open(getExportDataName(image.id, image.type), "w") as data_file:

            writer = csv.writer(data_file, quoting=csv.QUOTE_NONE)
        
            writer.writerow(['{0:d}'.format(math.trunc(x)) for x in image.data[0, :]])
        
    exportMetadata(image)

def exportRaw(image):

    if image.got_data == 1:
        with open(getExportDataName(image.id, image.type), "w") as data_file:

            writer = csv.writer(data_file, quoting=csv.QUOTE_NONE)
        
            for i in range(0, 256):
                writer.writerow(["{0:.2f}".format(x) for x in image.data[i, :]])

    exportMetadata(image)

def exportImage(image):

    if image.type == 1:

        exportRaw(image)

    if image.type >= 2 and image.type <= 8:

        exportBinning(image)

    elif image.type == 16:

        exportSums(image)

    elif image.type == 32:

        exportHistogram(image)

def exportCsv(data):

    if isinstance(data, HouseKeeping):

        exportHouseKeeping(data)

    elif isinstance(data, Image):

        exportImage(data)
