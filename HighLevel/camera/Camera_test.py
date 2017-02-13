import cv2
import numpy as np
from common import util
from common import color_pallete
import copy
import time
from CanvasCamera import Camera
from CameraException import *
from color_segmentation import color_segment





def correct_image(src_imset, painted_imset):
    """
    Generates an array of images, containing area that must be painted by color.
    Canvas color is not provided in the image sets, and so is interpolated.

    src_imset: image decomp set containing array of color channels as bin images
    painted_imset: image decomp set containing array of color channels as bin images
    """

    color_corrections = []
    canvas_corrections = []

    for image in range(len(painted_imset)):

        error_img = cv2.bitwise_xor(painted_imset[image], src_imset[image])

        paint_color = cv2.bitwise_and(error_img, painted_imset[image])
        color_corrections.append(paint_color)

        paint_color = cv2.bitwise_and(error_img, src_imset[image])
        canvas_corrections.append(paint_color)

    return color_corrections, canvas_corrections


cam = Camera(1)

boat = util.getFileByName("boat2.png", "../resources/images/input/")

# print warped_canvas


print "test"
img = cam.read_camera()
# cv2.imshow('orig', warped_canvas)
# util.display(warped_canvas)
# util.display(cam.read_camera())

dewarp_img = cam.dewarp(img)

a, w, h = dewarp_img.shape

dewarp_img = dewarp_img[70:w-250, 170:h-170]


time.sleep(0.1)

try:
    cam.generate_transform(dewarp_img)
    img_to_show = cam.get_canvas(dewarp_img)
except CameraTransformError:
    img_to_show = boat

# img_to_show = dewarp_img
util.display(img_to_show, "Painting canvas")


###
# paint paint paint paint paint
###

# Read in the image and dewarp it.
painted_image = cam.dewarp(cam.read_camera())

color_corrections, canvas_corrections = correct_image(boat, painted_image)

###
# paint the new thing
###

print "DONE"




#
# # warped_canvas = cv2.imread("CameraFeedback/1.png", cv2.IMREAD_UNCHANGED)
# warped_picture = cv2.imread("CameraFeedback/flask_mod.png", cv2.IMREAD_COLOR)
#
# src_img = util.getFileByNameNoAlpha("flask.png", "../resources/images/input/") #cv2.imread("CameraFeedback/fake.png", cv2.IMREAD_COLOR)
#
#
#
# # dewarped_canvas = dewarp(warped_canvas)
# # dewarped_picture = dewarp(warped_picture)
# dewarped_picture = warped_picture
# # src_img = dewarp(src_img)
#
#
#
# _, h, w = warped_picture.shape
#
# xinit = 430
# xlim = 370
# yinit = 130
# ylim = 660
#
# # dewarped_canvas = dewarped_canvas[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
# # segmented_picture = dewarped_picture[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
# # src_img = src_img[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
# segmented_picture = dewarped_picture
#
# util.display(segmented_picture)
# util.display(src_img)
#
#
# palette = color_pallete.buildPallete("blue green")
#
#
# colors, color_segments, segmented_image = color_segment(dewarped_picture, palette)
# colors_src, color_segments_src, segmented_image_src = color_segment(src_img, palette)
#
# paint_color_corrections, paint_canvas_corrections = correct_image(color_segments_src, color_segments)
#
# for elt in paint_color_corrections:
#     util.display(elt)
#
# for elt in paint_canvas_corrections:
#     util.display(elt)
#
# #  util.display(get_canvas(None, dewarped_canvas)) # Shit's broken - Odell needs LED's
