import numpy
import copy

def pixelActive(image, x, y):

    if (x < 1) or (x > 256):
        return -1

    if (y < 1) or (y > 256):
        return -1

    if (image.data[x, y] > 0):
        return 1
    else:
        return 0

def filterImage(image):

    filtered_image = copy.copy(image)
    filtered_image.data = numpy.zeros(shape=[256, 256])

    for i in range(255):

        for j in range(255):

            if (pixelActive(image, i, j) and not pixelActive(image, i, j-1) and not pixelActive(image, i, j+1) and not pixelActive(image, i-1, j-1) and not pixelActive(image, i-1, j) and not pixelActive(image, i-1, j+1) and not pixelActive(image, i+1, j-1) and not pixelActive(image, i+1, j) and not pixelActive(image, i+1, j+1)):

                filtered_image.data[i, j] = image.data[i, j]

    return filtered_image
