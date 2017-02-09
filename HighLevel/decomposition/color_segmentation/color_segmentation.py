from common import util
import numpy as np
import cv2
from scipy.cluster.vq import vq

# BLUE, GREEN, RED is the order for OpenCV pixel color values.

def classify_px(px, colors):
    # color_norm = []
    # for color in range(0, len(colors)):
    #     color_norm.append(np.linalg.norm(px-colors[color]))

    # # Return the index value of the color that has the smallest error compared to the pixel
    # return color_norm.index(min(color_norm))

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
    best_hue = 0
    best_diff = abs(h-hues[0])

    for index in range(1, len(hues)):
        diff = abs(h-hues[index])
        if diff<best_diff:
            best_diff = diff
            best_hue = index
    return best_hue

# TODO: Make this do the thing Nick said with canvas colors not beoing output
def color_segment(image, paint_colors,canvas_color = [255,255,255]):

    rows, cols, _ = image.shape

    colors = np.concatenate((np.array([canvas_color]),np.array(paint_colors)))

    # @TODO, this should use image.item and image.itemset as per below link, to speed things up.
    # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_core/py_basic_ops/py_basic_ops.html
    # For each pixel line in the image
    # for pixel_line in range(0, len(image)):
    #     #For each pixel in the line of pixels
    #     for pixel in range(0, len(image[pixel_line])):
    #         # Classify the pixel and recolor the pixel to the closest color
    #         color_val = classify_px((image[pixel_line])[pixel], colors)
    #         new_px = colors[color_val]
    #         (image[pixel_line])[pixel] = new_px

    # for i in range(rows):
    #     for j in range(cols):
    #         image[i,j]=classify_px(image[i,j], colors)
    #         # color = classify_px(np.array([image.item(i,j,0),image.item(i,j,1),image.item(i,j,2)]), colors)
    #         # image.itemset((i,j,0),color[0])
    #         # image.itemset((i,j,1),color[1])
    #         # image.itemset((i,j,2),color[2])

    pixel = np.reshape(image,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors)

    # reshaping the result of the quantization
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))
    image = colors[centers_idx]
    image = np.uint8(image)

    util.output(util.open_image(util.close_image(image)))
    bin_images = [] # The 1-color images.

    for index in range(0, len(paint_colors)):
        # Create a deep copy of the image
        bin_image = 255-np.zeros((rows,cols,1), np.uint8)
        bin_image[np.where((centers_idx == index+1))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.

    bin_image = 255-np.zeros((rows,cols,1), np.uint8)
    bin_image[np.where((centers_idx == 0))] = [0]

    return [image, bin_images, bin_image]

def color_segment_hsv(image, paint_colors, canvas_color = [255,255,255]):
    rows, cols, _ = image.shape

    hsv_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    hsv_paints = cv2.cvtColor(np.uint8([paint_colors]),cv2.COLOR_BGR2HSV)[0].tolist()
    hsv_canvas = cv2.cvtColor(np.uint8([[canvas_color]]),cv2.COLOR_BGR2HSV)[0][0].tolist()

    colors=[canvas_color]
    colors.extend(paint_colors)

    hsv_colors=[hsv_canvas]
    hsv_colors.extend(hsv_paints)

    h,s,v = cv2.split(np.uint8([hsv_colors]))
    h=h[0]

    for i in range(rows):
        for j in range(cols):
            image[i,j]=colors[classify_hsv(hsv_image.item(i,j,0), h)]

    print "generating images"
    bin_images = [] # The 1-color images.

    for index in range(0, len(paint_colors)):
        # Create a deep copy of the image
        bin_image = 255-np.zeros((rows,cols,1), np.uint8)
        bin_image[np.where((image == paint_colors[index]).all(axis = 2))] = [0]
        bin_image = util.open_image(bin_image)
        bin_image = util.close_image(bin_image)
        bin_images.append(bin_image) # Add to the list of color specific images.

    bin_image = 255-np.zeros((rows,cols,1), np.uint8)
    bin_image[np.where((image == canvas_color).all(axis = 2))] = [0]
    bin_image = util.open_image(bin_image)
    bin_image = util.close_image(bin_image)
    return [image, bin_images, bin_image]