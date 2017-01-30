
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
import cv2
import copy
from HighLevel.common import util
import numpy as np
# BLUE, GREEN, RED is the order for OpenCV pixel color values.

def classify_px(px, colors):
    color_norm = []
    for color in range(0, len(colors)):
        color_norm.append(np.linalg.norm(px-colors[color]))

    # Return the index value of the color that has the smallest error compared to the pixel
    return color_norm.index(min(color_norm))


def color_segment(image_name, colors):
    image = util.getFileByName(image_name)

    rows, cols, _ = image.shape


    # For each pixel line in the image
    for pixel_line in range(0, len(image)):
        #For each pixel in the line of pixels
        for pixel in range(0, len(image[pixel_line])):
            # Classify the pixel and recolor the pixel to the closest color
            color_val = classify_px((image[pixel_line])[pixel], colors)
            new_px = colors[color_val]
            (image[pixel_line])[pixel] = new_px

    util.display(image)

    color_images = [] # The 1-color images.

    for color in range(0, len(colors)):
        # Create a deep copy of the image
        color_image = np.zeros((rows,cols,1), np.uint8)
        color_image[:] = [255]

        color_image[np.where((image == colors[color]).all(axis = 2))] = [0]


        color_images.append(color_image) # Add to the list of color specific images.

    # This is just some example/cruft, this should never be implemented here.
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    # for cimage in range(0, len(color_images)):
    #     color_images[cimage] = cv2.morphologyEx(color_images[cimage], cv2.MORPH_CLOSE, kernel, iterations=1)
    #     color_images[cimage] = cv2.morphologyEx(color_images[cimage], cv2.MORPH_OPEN, kernel, iterations=1)


    return [colors, color_images, [image]]

