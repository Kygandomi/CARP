import cv2
import copy
import numpy as np

def grayscale_segment(grayscale_image, paint_colors, scale = 4):
    #paint_colors = 4 # The number of greys to segment the image into, INCLUDING black and white
    gradient = grayscale_image

    cols, rows, channels = gradient.shape

    gradient = cv2.resize(gradient, (rows/scale, cols/scale))

    thresholded_images = []
    thresh_vals = []

    for x in range (0, paint_colors):
        threshval = (float(x)/float(paint_colors))*255.0
        thresh_vals.append(threshval)
        ret,thresh = cv2.threshold(gradient,threshval,255,cv2.THRESH_BINARY)
        thresholded_images.append(thresh)

    for image_to_recolor in range(0, len(thresholded_images)):
        image = thresholded_images[image_to_recolor]
        grayval = thresh_vals[image_to_recolor]
        # For each threshed image that has area that is black, turn it to the appropriate grey.
        image[np.where((image == [0,0,0]).all(axis = 2))] = [grayval,grayval,grayval]
        thresholded_images[image_to_recolor] = image

    threshed_image = copy.deepcopy(thresholded_images[0])

    for x in range(len(thresholded_images), 0, -1):
        img = thresholded_images[x-1]

        # Super inefficient, slow.
        # TODO Change this to use some kind of pixel condition like when we're creating the images.
        for col in range(0, rows/scale):
            for row in range(0, cols/scale):
                # If the BRG sum value is greater, then overwrite.
                if sum(threshed_image[row][col]) > sum(img[row][col]):
                    threshed_image[row][col] = img[x][col]

    layer_images = [threshed_image]

    for thresh in thresh_vals:
        thresh = int(thresh)
        image_to_segment = copy.deepcopy(threshed_image)
        image_to_segment[np.where((image_to_segment != [thresh,thresh,thresh]).all(axis = 2))] = [255,255,255]
        layer_images.append(image_to_segment)
    # If you want to output the images here.
    #for x in range(0,len(layer_images)):
    #    util.save(layer_images[x], "img" + str(x))

    return layer_images[0], layer_images[1::]