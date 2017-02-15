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
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from decomposition.decomp_color.decomp_color import *
from recomposition.skeleton.skeletonRecompose import *
from common.util import *
from common import color_pallete

from time import sleep
import cv2
from camera.CanvasCamera import Camera
from camera.CameraException import *



# ##################################################################
# ##########################  SETUP COMMUNICATIONS  ################
# ##################################################################
print "Setup"

# Establish Serial Connection with the Arduino
baud = 115200
ports_list = ['COM8','COM3','/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9', '/dev/cu.usbmodem1421']
could_connect = False
for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if(arduino_ser.connect()):
		print "Serial Comm Connected"
		could_connect = True
		break

# Comment back in when we have an actual serial port
if not could_connect :
	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)


gantry_offX = -70
gantry_offY = -200

##################################################################
# # INIT PAINTING OBJECT
paint_routine = PaintOrders.paint_orders(arduino_ser)


##################################################################

cam = Camera(1)

boat = util.readImage("circle.png", "resources/images/input/")

img = cam.read_camera()
util.save(img, "01_camera_read")

dewarp_img = cam.dewarp(img)
a, w, h = dewarp_img.shape
util.save(dewarp_img, "02_dewarp_camera_read")



try:
	cam.generate_transform(dewarp_img)
	img_to_show = cam.get_canvas(dewarp_img)
except CameraTransformError:
	img_to_show = boat


util.save(img_to_show, "03_camera_transform")


##################################################################
# DECOMP
# For the future, if we don't want to use the boat.
#desiredImg = readImage("medusa_raft.png", type_flag=1)
desiredImg = boat

white = [255,255,255]

segmented_image, [colors,color_segments], [canvas,canvas_segment]  = \
	decompose(desiredImg, 2,[], color_pallete.white)

util.save(segmented_image, "04_color_desegmented_image")


##################################################################
## Move gantry into paint position
# paint_routine.moveGantry(0, 0)

##################################################################

# Recomposers to use

# Recomp and Paint
for index in range(len(color_segments)):
	print "Index ", index
	img = color_segments[index]

	print "Fetching new brush"
	# paint_routine.getBrush(index)

	print "Recomposition"
	recomposer = skeletonRecomposer(img, [])
	LLT = recomposer.recompose()

	print "LLT to Paint: ", LLT
	util.save(testLLT(LLT,3), "circle_from_llt")

	print "Let's Paint a Picture ~"
	# paint_routine.Paint(LLT)

	print "LLT Finished "

# paint_routine.returnToStart()
print "Routine Complete, Enjoy ! "

##################################################################

painted_image = cam.dewarp(cam.read_camera())
util.save(painted_image, "05_painting")

painting = cam.get_canvas(painted_image)
util.display(painting, "painting")

palette = color_pallete.build("black white")

segmented_image_act, [colors,color_segments_act], [canvas,canvas_segment]  \
    = decompose(boat, 0,palette, color_pallete.white)
segmented_image, [colors,color_segments_src], [canvas,canvas_segment]  \
    = decompose(painting, 0,palette, color_pallete.white)

for elt in range(0, len(color_segments_src)):
	color_segments_src[elt] = resize_with_buffer(color_segments_src[elt], color_segments_act[elt])

correction_segments, canvas_corrections = cam.correct_image(color_segments_src,color_segments_act)
for image in correction_segments:
	img4 = open_image(image)
	output(img4)
#
# for image in canvas_corrections:
# 	img4 = open_image(image)
# 	output(img4)


##################################################################

######
# painting the things

# Recomp and Paint
for index in range(len(correction_segments)):
	print "Index ", index
	img = correction_segments[index]
	img = open_image(img)

	print "Fetching new brush"
	# paint_routine.getBrush(index)

	print "Recomposition"
	recomposer = iterativeErosionRecomposer(img, [3])
	LLT = recomposer.recompose()

	print "LLT to Paint: ", LLT
	testLLT(LLT,3)

	print "Let's Paint a Picture ~"
	# paint_routine.Paint(LLT)

	print "LLT Finished "

# paint_routine.returnToStart()
print "Routine Complete, Enjoy ! "


img = cam.read_camera()
util.save(img, "06_camera_read_final")

dewarp_img = cam.dewarp(img)
a, w, h = dewarp_img.shape
# dewarp_img = dewarp_img[70:w-250, 170:h-170]
util.save(dewarp_img, "07_dewarp_camera_read_final")

