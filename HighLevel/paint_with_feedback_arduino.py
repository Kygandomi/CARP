#! /usr/bin/env python
# MQP -- CARP Project

from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
from paint_with_pmd import ethernet_communication as eth_comm

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *

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

		if open_images: img = open_image(img)

		display(img)

		print "Fetching new brush"
		painter.getBrush(index)

		print "Recomposition"
		recomposer = skeletonRecomposer(img, [])
		LLT = recomposer.recompose()
		LLT = cam.canvas_to_gantry(LLT)

		# print "LLT to Paint as been saved to disc: ", LLT
		# util.output(testLLT(LLT,3), "Drawn LLT")

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
		raise Exception('Could not connect...')

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
		raise Exception('Could not connect...')
	# Sleep to verify a solid connection
	sleep(1)
	return pmd_com

def calculate_error_threshold():
	return True

########################################################################################################################
## SETUP COMMUNICATIONS
########################################################################################################################
print "Connecting to Controller..."
com_obj = setup_communications()

########################################################################################################################
## INITIALIZATION OF OBJECTS AND OTHER MISC SETUP REQUIREMENTS
########################################################################################################################
print "Initialization" 
# Create Paint object and obtain desired image
paint_routine = PaintOrders.paint_orders(com_obj)
palette = color_pallete.build("red yellow white")
desiredImg = util.readImage("boat2.png", "resources/images/input/")

# Initialize Camera Object
cam = Camera(0)

# Remove any bad frames
for i in range(0,4):
	read_img = cam.read_camera()

# Dewarp and Prepare image for Processing
dewarp_img = cam.dewarp(read_img)
a, w, h = dewarp_img.shape

dewarp_img = cv2.resize(dewarp_img, (0,0),fx=2,fy=2)

cam.generate_transform(dewarp_img)
img_to_show = cam.get_canvas(dewarp_img)
display(img_to_show)

desiredImg = util.resize_with_buffer(desiredImg,img_to_show)
display(desiredImg)

# Initial Decomposition of image
segmented_image, [colors,color_segments], [canvas,canvas_segment]  = decompose(desiredImg, 4,[], color_pallete.white)

display(segmented_image)

# Inital Paint Sequence for Image
paint_imageset(color_segments, paint_routine, cam)

########################################################################################################################
# FEEDBACK LOOP
########################################################################################################################
# While the error is too high
while calculate_error_threshold():
	print "Feedback Loop..."
	# Get a new canvas image
	painting = cam.get_canvas(cam.dewarp(cam.read_camera()))
	util.save(painting, "PaintingFileAtStartOfFeedbackLoop")
	rows, cols, _ = painting.shape

	# TODO Remember to remove this when we move to PMD and/or fix the transform issue
	M = np.float32([[1,0,12],[0,1,21]])
	painting = cv2.warpAffine(painting,M,(cols,rows))

	# Decompose the desired and canvas image
	segmented_image_act, [_,color_segments_src], [_,_] = decompose(desiredImg, 0,palette, color_pallete.white)
	_, [_,color_segments_act], [_,_] = decompose(painting, 0,palette, color_pallete.white)

	# Generate correction images
	correction_segments, canvas_corrections = cam.correct_image(color_segments_src,color_segments_act)

	# Paint Corrections
	paint_imageset(correction_segments, paint_routine, cam ,open_images = True)
