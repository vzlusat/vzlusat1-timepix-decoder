# generate respective file names for the binary image files using image_id and the type of the image
def getFileName(image_id, image_type, path="images_bin/"):

    return path+str(image_id)+"_{0:02d}.pkl".format(image_type) 

def getHkFileName(images_taken, time_since_boot, boot_count):

    return "images_bin/"+str(images_taken)+"_"+str(boot_count)+"_{0:05d}_h.pkl".format(time_since_boot) 

def getExportDataName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_{0:02d}.txt".format(image_type) 

def getExportDescriptionFileName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_{0:02d}.txt.dsc".format(image_type) 

def getExportMetadataName(image_id, image_type):

    return "images_csv/"+str(image_id)+"_{0:02d}.metadata.txt".format(image_type) 

def getExportHkName(images_taken, time_since_boot, boot_count):

    return "images_csv/"+str(images_taken)+"_"+str(boot_count)+"_{0:05d}.txt".format(time_since_boot) 
