import numpy
import copy

def pixelActive(image, x, y):

    if (x < 0) or (x > 255):
        return -0

    if (y < 0) or (y > 255):
        return -0

    if (image.data[x, y] > 0):
        return 1
    else:
        return 0

def countNeighbours(image, x, y):

    neighbours = 0

    if pixelActive(image, x-1, y):
        neighbours += 1
    if pixelActive(image, x+1, y):
        neighbours += 1
    if pixelActive(image, x, y-1):
        neighbours += 1
    if pixelActive(image, x, y+1):
        neighbours += 1

    return neighbours

def filterImage(image):

    filtered_image = copy.copy(image)
    filtered_image.data = numpy.zeros(shape=[256, 256])

    for i in range(255):

        for j in range(255):

            active_around = countNeighbours(image, i, j)

            # if our pixel is active and there are no active pixel around
            if (pixelActive(image, i, j)) and active_around == 0: 
                filtered_image.data[i, j] = image.data[i, j]

            # if our pixel is active and there is you active pixel around
            if (pixelActive(image, i, j)) and active_around == 1: 

                if (pixelActive(image, i-1, j) and countNeighbours(image, i-1, j) == 1) or \
                (pixelActive(image, i+1, j) and countNeighbours(image, i+1, j) == 1) or \
                (pixelActive(image, i, j-1) and countNeighbours(image, i, j-1) == 1) or \
                (pixelActive(image, i, j+1) and countNeighbours(image, i, j+1) == 1):
                    filtered_image.data[i, j] = image.data[i, j]

    return filtered_image
