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

def paint_imageset(segments, painter, cam, open_images = False):
	for index in range(len(segments)):
		print "Index ", index
		img = segments[index]

		if open_images: img = open_image(img, kernel_radius = 5)

		print "Recomposition"
		
		# recomposer = skeletonRecomposer(img, [])
		# recomposer = iterativeErosionRecomposer(img, [1])
		recomposer = blendedRecomposer(img, [3]) 
		LLT = recomposer.recompose()
		LLT = util.arrangeLLT(LLT)
		# print LLT
		# display(img)
		# display(testLLT(LLT,1,img.shape))
		LLT = cam.canvas_to_gantry(LLT)

		# print "LLT to Paint as been saved to disc: ", LLT
		# util.output(testLLT(LLT,3), "Drawn LLT")
		print "Fetching new brush"
		painter.getBrush(index) 

		print "Painting LLT..."
		painter.Paint(LLT)

		print "LLT Completed."

	painter.returnToStart()
	sleep(5)
	print "First pass has been completed."

def setup_communications():
	# Establish Serial Connection with the Arduino
	baud = 115200
	ports_list = ['COM8','COM3','/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9', '/dev/cu.usbmodem1421']
	could_connect = False

	# Seek arduino connection
	for i in range(len(ports_list)):
		port = ports_list[i]
		ser_obj = ser_comm.serial_comms(port, baud)
		if ser_obj.connect():
			print "Serial Comm Connected"
			could_connect = True
			break

	# Comment back in when we have an actual serial port
	if not could_connect :
		raise Exception('Could not connect via Serial')

	# Sleep to verify a solid connection
	sleep(1)
	return ser_obj

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
# Create Paint object and obtain desired image

desiredImg = util.readImage("boat2.png", "resources/images/input/")
n_colors = 4
palette = color_pallete.build("black white red yellow")

# Initialize Camera Object
cam = Camera([1,0])

# TODO: If you can't connect to camera, assume canvas shape is 8.5x11 starting at 0,0
if not cam.isOpened():
	raise Exception('Could not connect to Camera')

display(cam.get_dewarped())
cam.generate_transform()
img_to_show = cam.get_canvas()

display(img_to_show)

desiredImg = util.resize_with_buffer(desiredImg,img_to_show)

# Initial Decomposition of image
pallete = [[0,0,0], [25,255,255], [255,255,255], [0,0,255]]
segmented_image, [colors,color_segments,indeces], [canvas,canvas_segment,canvas_index]  = decompose(desiredImg, n_colors, pallete, color_pallete.colorMap["white"])

print "outputted colors: ", colors
print "outputted indeces: ", indeces
# Todo: Use indeces to send robot to proper paint well

display(segmented_image)

########################################################################################################################
## SETUP COMMUNICATIONS
########################################################################################################################
print "Connecting to Controller..."
com_obj = setup_communications_eth()
paint_routine = PaintOrders.paint_orders(com_obj)

# Inital Paint Sequence for Image
paint_imageset(color_segments, paint_routine, cam,True)

########################################################################################################################
# FEEDBACK LOOP
########################################################################################################################
# While the error is too high
while calculate_error_threshold():
	print "Feedback Loop..."
	# Get a new canvas image
	painting = cam.get_canvas()
	# util.save(painting, "PaintingFileAtStartOfFeedbackLoop")
	rows, cols, _ = painting.shape

	# TODO Remember to remove this when we move to PMD and/or fix the transform issue
	# M = np.float32([[1,0,12],[0,1,21]])
	# painting = cv2.warpAffine(painting,M,(cols,rows))

	# Decompose the desired and canvas image
	# Todo: Tie colors in actual paint wells to colors outputted by Kmeans
	_, [_ ,color_segments_src], [_,_] = decompose(desiredImg, 0,palette, color_pallete.colorMap["white"])
	_, [paint_colors, color_segments_act], [_,_] = decompose(painting, 0,palette, color_pallete.colorMap["white"])

	print "***************************************"
	print "Paint colors: ", paint_colors 

	# display(painting,"Canvas Image")
	# for frame in color_segments_act:
	# 	display(frame,"actual bin_img")

	# Generate correction images
	correction_segments, canvas_corrections = cam.correct_image(color_segments_src,color_segments_act)

	# for frame in correction_segments:
	# 	display(frame,"corrections")

	# Paint Correctionst
	paint_imageset(correction_segments, paint_routine, cam ,open_images = True )
