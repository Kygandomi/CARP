#! /usr/bin/env python
# MQP -- CARP Project
#
# This script takes an input image and 
# paints it with the robot with the current
# Arduino low level and incorporates visual feedback
# into the process

# Import Dependencies
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
from recomposition.skeleton.skeletonRecompose import *
from common.util import *
from time import sleep
import cv2

#############################################################
# returns error and region of difference
def calculate_error(decomp_input, decomposed_canvas):
	num_pixels_different = 0
	regions_to_paint = {}

	# Just a really awful pixel by pixel comparison
	for index in range(0, len(decomp_input)): 
		decomp_area = decomp_input[index]
		canvas_area = decomposed_canvas[index]
		(area_width, area_height) = decomp_area.shape

		paint_region = "matrix of same size decomp area"
		paint_val = 255

		for x in range(0, area_width):
			for y in range(0, area_height):
				val = decomp_area[x][y]
				if val != 255:
					paint_val = val
					canvas_val = canvas_area[x][y]

					if canvas_val != paint_val:
						num_pixels_different += 1
						paint_region[x][y] = paint_val


		if not paint_val in regions_to_paint.keys() and paint_val != 255:
			regions_to_paint[paint_val] = paint_region[x][y]

	return num_pixels_different, regions_to_paint

def get_canvas_image(video_feed):
	ret, canvas_image = video_feed.read()
	return canvas_image

#############################################################

# Setup
# initialize sercomm to arduino ...
camera = cv2.VideoCapture(0)
similarity_threshold = 50
num_regions = 1

# Paint Orders Object
paint_routine = PaintOrders.paint_orders(arduino_ser)

# take in image to process
input_image = 'resources/images/input/pig.png'

# take in a canvas image
canvas_image = get_canvas_image(camera)

# decompose input image
decomposed_input = 0

# decompose canvas image
decomposed_canvas = 0

# Calculate error and obtain regions of differnce
error, diff_regions = calculate_error(decomposed_input, decomposed_canvas)

# while the error is valid and is not less than the similarity threshold
while(error > 0 and error < similarity_threshold):
	LLT_regions = []

	# Recompose regions of difference
	for paint_color, region in diff_regions.items(): 
		recomposer = skeletonRecomposer(region, [])
		recomp_LLT = recomposer.recompose()
		LLT_regions += recomp_LLT

	# Maybe later we can sort the LLTs into an ordered list ?
	# Paint LLTs of each region
	for LLT in LLT_regions:
		paint_routine.Paint(LLT)

	# Update canvas variables
	canvas_image = get_canvas_image(camera)
	decomposed_canvas = 0

	error, diff_regions = calculate_error(decomposed_input, decomposed_canvas)

