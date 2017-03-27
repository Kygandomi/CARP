from common import util
import numpy as np
import cv2
from scipy.cluster.vq import vq

# BLUE, GREEN, RED is the order for OpenCV pixel color values.

def classify_px(px, colors):
    """
    Classifies a pixel to the closest color given in colors.
    """

    best_color = colors[0]
    best_norm = np.linalg.norm(px-colors[0])

    for index in range(1, len(colors)):
        color = colors[index]
        color_norm = np.linalg.norm(px-color)
        if color_norm<best_norm:
            best_norm = color_norm
            best_color = color
    return best_color


def classify_hsv(h,hues):
    """
    HSV-space pixel classification based on hues and hue similarity.
    """

    best_hue = 0
    best_diff = abs(h-hues[0])

    for index in range(1, len(hues)):
        diff = abs(h-hues[index])
        if diff<best_diff:
            best_diff = diff
            best_hue = index
    return best_hue

# TODO: Make this do the thing Nick said with canvas colors not being output
def color_segment(image, paint_colors,canvas_color = [255,255,255]):
    """
    Segment an image based on the RBG color.
    :param image: The image to be segmented
    :param paint_colors: The available colors to segment into
    :param canvas_color: The color of the canvas
    :return: [Classified image, [binary images for each color], canvas binary image]
    """

    rows, cols, _ = image.shape

    colors = np.concatenate((np.array([canvas_color]),np.array(paint_colors)))

    pixel = np.reshape(image,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors)

    # reshaping the result of the quantization
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))
    image = colors[centers_idx]
    image = np.uint8(image)

    util.output(util.open_image(util.close_image(image)))
    bin_images = [] # The 1-color images.

    # Generate the binary images that represent different colors.
    for index in range(0, len(colors)):
        # Create a deep copy of the image
        bin_image = 255-np.zeros((rows,cols,1), np.uint8)
        #bin_image[np.where((image == paint_colors[index]).all(axis = 2))] = [0]
        bin_image[np.where((centers_idx == index))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.

    bin_image = bin_images.pop(0)

    return [image, bin_images, bin_image]

def color_segment_hsv(image, paint_colors, canvas_color = [255,255,255]):
    """
    Segments colors based on HSV space, rather than RGB values.
    :param image: The image to be segmented
    :param paint_colors: The available colors to segment into
    :param canvas_color: The color of the canvas
    :return: [Classified image, [binary images for each color], canvas binary image]
    """

    rows, cols, _ = image.shape

    # Convert images to their HSV-space representations
    hsv_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    hsv_paints = cv2.cvtColor(np.uint8([paint_colors]),cv2.COLOR_BGR2HSV)[0].tolist()
    hsv_canvas = cv2.cvtColor(np.uint8([[canvas_color]]),cv2.COLOR_BGR2HSV)[0][0].tolist()

    colors=[canvas_color]
    colors.extend(paint_colors)

    hsv_colors=[hsv_canvas]
    hsv_colors.extend(hsv_paints)

    h,s,v = cv2.split(np.uint8([hsv_colors]))
    h=h[0]

    # Using the HSV classifier, classify each px
    for i in range(rows):
        for j in range(cols):
            image[i,j]=colors[classify_hsv(hsv_image.item(i,j,0), h)]

    bin_images = [] # The 1-color images.

    # Generate the binary images that represent each color
    for index in range(0, len(paint_colors)):
        bin_image = 255-np.zeros((rows,cols,1), np.uint8)
        bin_image[np.where((image == paint_colors[index]).all(axis = 2))] = [0]

        bin_images.append(bin_image) # Add to the list of color specific images.

    bin_image = 255-np.zeros((rows,cols,1), np.uint8)
    bin_image[np.where((image == canvas_color).all(axis = 2))] = [0]

    return [image, bin_images, bin_image]