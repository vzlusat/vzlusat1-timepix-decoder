# generate respective file names for the binary image files using image_id and the type of the image
def getFileName(image_id, image_type, path="images_bin/"):

    return path+str(image_id)+"_{0:02d}.pkl".format(image_type) 

def getHkFileName(images_taken, time_since_boot, boot_count):

    return "images_bin/"+str(images_taken)+"_"+str(boot_count)+"_{0:05d}_h.pkl".format(time_since_boot) 

def getHRFileType(imagetype):

    if imagetype == 1:
        name = "fullres"
    elif imagetype == 2:
        name = "binning8"
    elif imagetype == 4:
        name = "binning16"
    elif imagetype == 8:
        name = "binning32"
    elif imagetype == 16:
        name = "sums"
    elif imagetype == 32:
        name = "histogram"

    return name

def getExportDataName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_"+getHRFileType(image_type)+".txt".format(image_type) 

def getExportDescriptionFileName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_"+getHRFileType(image_type)+".txt.dsc"

def getExportMetadataName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_"+getHRFileType(image_type)+".metadata.txt".format(image_type) 

def getExportHkName(images_taken, time_since_boot, boot_count):

    return "images_csv/housekeeping_"+str(images_taken)+"_"+str(boot_count)+"_{0:05d}.txt".format(time_since_boot) 
