from common import util
import numpy as np

# BLUE, GREEN, RED is the order for OpenCV pixel color values.

def classify_px(px, colors):
    color_norm = []
    for color in range(0, len(colors)):
        color_norm.append(np.linalg.norm(px-colors[color]))

    # Return the index value of the color that has the smallest error compared to the pixel
    return color_norm.index(min(color_norm))

# TODO: Make this do the thing Nick said with canvas colors not beoing output
def color_segment(image, colors):

    rows, cols, _ = image.shape

    # @TODO, this should use image.item and image.itemset as per below link, to speed things up.
    # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_core/py_basic_ops/py_basic_ops.html
    # For each pixel line in the image
    for pixel_line in range(0, len(image)):
        #For each pixel in the line of pixels
        for pixel in range(0, len(image[pixel_line])):
            # Classify the pixel and recolor the pixel to the closest color
            color_val = classify_px((image[pixel_line])[pixel], colors)
            new_px = colors[color_val]
            (image[pixel_line])[pixel] = new_px

    util.save(util.open_image(util.close_image(image)))

    color_images = [] # The 1-color images.

    for color in range(0, len(colors)):
        # Create a deep copy of the image
        color_image = np.zeros((rows,cols,1), np.uint8)
        color_image[:] = [255]

        color_image[np.where((image == colors[color]).all(axis = 2))] = [0]

        color_images.append(color_image) # Add to the list of color specific images.

    return [colors, color_images, [image]]

