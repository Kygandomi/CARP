#! /usr/bin/env python
# MQP -- CARP Project

from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
from paint_with_pmd import ethernet_communication as eth_comm

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *
from recomposition.blendedRecompose import *

from decomposition.decomp_color.decomp_color import *

from camera.CanvasCamera import Camera
from camera.CameraException import *

from common.util import *
from common import color_pallete

from time import sleep
import cv2

def paint_imageset(segments, painter, cam, color_indeces, open_images = False):
	for index in range(len(segments)):
		print "Index ", index
		img = segments[index]

		if open_images: img = open_image(img, kernel_radius = 5)

		print "Recomposition"
		
		# recomposer = skeletonRecomposer(img, [])
		# recomposer = iterativeErosionRecomposer(img, [1])
		recomposer = blendedRecomposer(img, [3]) 
		LLT = recomposer.recompose()
		if len(LLT)>0:
			LLT = util.arrangeLLT(LLT)
			# display(img)
			display(testLLT(LLT,1,img.shape))
			LLT = cam.canvas_to_gantry(LLT)

			# print "LLT to Paint as been saved to disc: ", LLT
			# util.output(testLLT(LLT,3), "Drawn LLT")
			print "Fetching new brush"
			painter.getBrush(color_indeces[index])

			print "Painting LLT..."
			painter.Paint(LLT)

			print "LLT Completed."

	painter.returnToStart()
	sleep(5)
	print "First pass has been completed."

def setup_communications_eth():
	# Establish Serial Connection with the Arduino
	ip = '192.168.178.7'
	port = 1234
	pmd_com = eth_comm.ethernet_comms(ip, port)

	connected = False

	#while not connected:
	connected = pmd_com.connect()
	if not connected:
		raise Exception('Could not connect via Ethernet')
	# Sleep to verify a solid connection
	sleep(1)
	return pmd_com

def calculate_error_threshold():
	return True

########################################################################################################################
## INITIALIZATION OF OBJECTS AND OTHER MISC SETUP REQUIREMENTS
########################################################################################################################
print "Initialization" 
# Select Desired Image
desiredImg = util.readImage("boat2.png", "resources/images/input/")

# Input Color Configurations
n_colors = 4
canvas_color = color_pallete.colorMap["white"]
pallete = color_pallete.build("black red yellow")

# Initialize Camera Object
cam = Camera([1,0])

# TODO: If you can't connect to camera, assume canvas shape is 8.5x11 starting at 0,0
if not cam.isOpened():
	raise Exception('Could not connect to Camera')

# Perform Image Transformations to prepare canvas for painting
display(cam.get_dewarped())

cam.generate_transform()
img_to_show = cam.get_canvas()
display(img_to_show)

desiredImg = util.resize_with_buffer(desiredImg,img_to_show)

# Initial Decomposition of the input Image
segmented_image, color_segments, colors, indeces = decompose(desiredImg, pallete,n_colors,canvas_color=canvas_color)

print "outputted colors: ", colors
print "outputted indeces: ", indeces

display(segmented_image, "Segmented Image")

########################################################################################################################
## SETUP COMMUNICATIONS
########################################################################################################################
print "Connecting to Controller..."
com_obj = setup_communications_eth()
paint_routine = PaintOrders.paint_orders(com_obj)

########################################################################################################################
# FEEDBACK LOOP
########################################################################################################################
# While the error is too high
while calculate_error_threshold():
	print "Feedback Loop..."
	
	# Get a canvas image
	painting = cam.get_canvas()

	# Segment the canvas image
	segmented_image_act, color_segments_act, paint_colors, pallete_indeces = decompose(painting, pallete,-1,canvas_color=canvas_color)

	print "***************************************"
	print "Paint colors: ", paint_colors 
	print "Pallete Indeces: ", pallete_indeces

	# Generate corrections for canvas image
	correction_segments, canvas_corrections = cam.correct_image(color_segments,color_segments_act)

	# Display for debugging
	display(segmented_image_act,"Segmented Canvas")
	for index in range(len(correction_segments)):
		display(correction_segments[index],str(paint_colors[index])+" at "+str(pallete_indeces[index]))

	# Paint Correctionst
	paint_imageset(correction_segments, paint_routine, cam, indeces,open_images = True )
