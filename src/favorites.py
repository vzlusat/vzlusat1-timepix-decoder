import numpy
import pickle
import os.path
from src.Image import *
from src.HouseKeeping import *
from src.baseMethods import *

global favorites
favorites = {}

file_name = "favorites.pkl"

def loadFavorites():

    global favorites
    # ask OS to locate the file
    if os.path.isfile(file_name):

        # if the file exists, open it
        with open(file_name, 'rb') as input:

            # load the object from the file
            try:
                favorites = pickle.load(input)
            except:
                print("file \"{}\" is corrupted".format(file_name))
                # create the new file
                favotires = {}
                saveFavorites()

    else:
        # create the new file
        favotires = {}
        saveFavorites()
        
def saveFavorites():

    global favorites

    # try to open the file
    with open(file_name, 'wb') as output:

        try:
            pickle.dump(favorites, output, pickle.HIGHEST_PROTOCOL)
        except:
            print("file \"{}\" could not be saved".format(file_name))

def isFavorite(data):

    global favorites

    key = ""

    if isinstance(data, Image):
        key=getFileName(data.id, data.type)
    elif isinstance(data, HouseKeeping):
        key=getHkFileName(data.images_taken, data.time_since_boot, data.boot_count)

    if key in favorites:
        return favorites[key]
    else:
        return False

def setFavorite(data, value):

    global favorites

    key = ""

    if isinstance(data, Image):
        key=getFileName(data.id, data.type)
    elif isinstance(data, HouseKeeping):
        key=getHkFileName(data.images_taken, data.time_since_boot, data.boot_count)

    favorites[key] = value

    saveFavorites()
