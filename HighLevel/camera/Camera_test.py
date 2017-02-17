import cv2
import numpy as np
from common import util
from common import color_pallete
import copy
import time
from CanvasCamera import Camera
from CameraException import *
from color_segmentation import color_segment
from decomp_color import *

cat = util.readImage("cat3.png", "../resources/images/input/")
boat = util.readImage("boat2.png", "../resources/images/input/")

cat = util.resize_with_buffer(cat, boat, padding_color=[255,255,5])

util.display(boat)
util.display(cat)

#
#
# circle_perf = util.readImage("circle.png", "../resources/images/input/")
# circle_actual = util.readImage("circle_painted2.png", "")
#
# h_perf, w_perf, _ = circle_perf.shape
# h_actual, w_actual, _ = circle_actual.shape
#
# perf_ratio = float(h_perf)/float(w_perf)
# actual_ratio =float(h_actual)/float(w_actual)
#
# buff = 0,0,0,0
#
# if perf_ratio > actual_ratio:
#     odd = False
#     if w_actual %2 == 1: # If we have an odd number of pixels
#         odd = True
#     buff_val = h_perf/actual_ratio
#     buff_val = ((h_perf/actual_ratio)-w_perf) /2
#     buff = 0,0, int(buff_val), int(buff_val) + int(odd)
# elif perf_ratio < actual_ratio:
#     odd = False
#     if w_actual %2 == 1: # If we have an odd number of pixels
#         odd = True
#     buff_val = w_perf/actual_ratio
#     buff_val = ((w_perf/actual_ratio)-h_perf) /2
#     buff = 0,0, int(buff_val), int(buff_val) + int(odd)
# #Else case where they are the same, they can just be reshaped immediately.
#
# top, bottom, left, right = buff
#
# img = cv2.copyMakeBorder(circle_perf, top, bottom, left, right, cv2.BORDER_CONSTANT,value=[255,255,255])
#
# img = cv2.resize(img, (w_actual, h_actual))
#
# cam = Camera(1)
# util.output(circle_actual, "circ act")
#
# palette = color_pallete.build("black white")
#
# segmented_image_act, [colors,color_segments_act], [canvas,canvas_segment]  \
#     = decompose(circle_actual, 0,palette, color_pallete.white)
# segmented_image, [colors,color_segments_src], [canvas,canvas_segment]  \
#     = decompose(img, 0,palette, color_pallete.white)
# util.output(color_segments_act[0], "act")
# util.output(color_segments_src[0], "src")
#
# util.output(segmented_image_act, "seg img")
#
# color_corrections, canvas_corrections = cam.correct_image(color_segments_src,color_segments_act)
#
# # print canvas_corrections
#
# util.output(255-canvas_corrections, "canvas_crrections")
#
# for c in color_corrections:
#     util.output (255-c, "color+scorection")
#
#
#
# cam = Camera(1)
#
# boat = util.getFileByName("boat2.png", "../resources/images/input/")
#
# # print warped_canvas
#
#
# print "test"
# img = cam.read_camera()
# util.display(img)
#
# # cv2.imshow('orig', warped_canvas)
# # util.display(warped_canvas)
# # util.display(cam.read_camera())
#
# dewarp_img = cam.dewarp(img)
#
# a, w, h = dewarp_img.shape
#
# dewarp_img = dewarp_img[70:w-150, 170:h-170]
#
#
# time.sleep(0.1)
#
# util.display(dewarp_img)
#
# try:
#     cam.generate_transform(dewarp_img)
#     img_to_show = cam.get_canvas(dewarp_img)
# except CameraTransformError:
#     img_to_show = boat
#
# # img_to_show = dewarp_img
# util.output(img_to_show, "01 Painting canvas, unpainted")
#
# util.display(boat)
#
#
#
# painted_image = cam.read_camera()
#
# util.output(img_to_show, "02 Painting")
#
# dewarped_painted_image = cam.dewarp(painted_image)
# dewarped_painted_image = dewarped_painted_image[70:w-150, 170:h-170]
#
# dewarped_painted_canvas = cam.get_canvas(dewarped_painted_image)
#
# util.output(dewarped_painted_canvas, "03 Painting on canvas")
#
# color_corrections, canvas_corrections = cam.correct_image(boat, painted_image)
#
# ###
# # paint the new thing
# ###
#
# print "DONE"




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
