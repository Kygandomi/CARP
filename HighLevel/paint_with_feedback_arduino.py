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
from decomposition.color_segmentation.color_segmentation import *
from decomposition.color_segmentation.color_quantization import *
from recomposition.skeleton.skeletonRecompose import *
from common.util import *
from time import sleep
import cv2
from CanvasCamera import Camera
from CameraException import *


##################################################################
##########################  SETUP COMMUNICATIONS  ################
##################################################################
print "Setup"

# Establish Serial Connection with the Arduino
baud = 115200
ports_list = ['COM8','COM3','/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9']
could_connect = False
for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if(arduino_ser.connect()):
		print "Serial Comm Connected"
		could_connect = True
		break

# Comment back in when we have an actual serial port
# if not could_connect :
# 	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)


##################################################################
# INIT PAINTING OBJECT
paint_routine = PaintOrders.paint_orders(arduino_ser)

## Move gantry out of the way
paint_routine.moveGantry(-50, 0)

# Camera setup, gantry is still away
##################################################################

cam = Camera(1)

boat = util.getFileByName("boat2.png", "../resources/images/input/")

img = cam.read_camera()
util.save(img, "01_camera_read")

dewarp_img = cam.dewarp(img)
a, w, h = dewarp_img.shape
dewarp_img = dewarp_img[70:w-250, 170:h-170]
util.save(img, "02_dewarp_camera_read")



try:
	cam.generate_transform(dewarp_img)
	img_to_show = cam.get_canvas(dewarp_img)
except CameraTransformError:
	img_to_show = boat

util.display(img_to_show, "Painting canvas")
util.save(img, "03_camera_transform")


##################################################################
# DECOMP
# For the future, if we don't want to use the boat.
#desiredImg = readImage("medusa_raft.png", type_flag=1)
desiredImg = boat

white = [255,255,255]

print "Quantization"
colors = color_quantize(desiredImg,4)
colors = remove_canvas(colors,white)

print "Segmentation"
segmented_image, color_segments, canvas_segment  = color_segment(desiredImg, colors, white)

util.save(img, "04_color_desegmented_image")


for image in color_segments:
	img4 = open_image(image)
	display(img4)


##################################################################
## Move gantry into paint position
paint_routine.moveGantry(0, 0)

##################################################################

# Recomposers to use
recompItErosion1 = iterativeErosionRecomposer(open_image(color_segments[0]), [3])
recompItErosion2 = iterativeErosionRecomposer(open_image(color_segments[1]), [2])
recompSkeleton = skeletonRecomposer(open_image(color_segments[2]), [])
recomposers = [recompItErosion1, recompItErosion2, recompSkeleton]

# Recomp and Paint
for index in range(len(color_segments)):
	print "Index ", index
	# img = color_segments[index]
	# img = open_image(img)

	print "Fetching new brush"
	paint_routine.getBrush(index)

	print "Recomposition"
	recomposer = recomposers[index]
	LLT = recomposer.recompose()

	print "LLT to Paint: ", LLT
	testLLT(LLT,3)

	print "Let's Paint a Picture ~"
	paint_routine.Paint(LLT)

	print "LLT Finished "

paint_routine.returnToStart()
print "Routine Complete, Enjoy ! "

##################################################################
## Move gantry out of the way
paint_routine.moveGantry(-50, 0)

##################################################################

painted_image = cam.dewarp(cam.read_camera())
util.save(img, "05_painting")


correction_segments, canvas_correction_segment = cam.correct_image(segmented_image, painted_image)
for image in correction_segments:
	img4 = open_image(image)
	display(img4)


##################################################################
## Move gantry out of the way
paint_routine.moveGantry(0, 0)

##################################################################

######
# painting the things

# Recomp and Paint
for index in range(len(correction_segments)):
	print "Index ", index
	img = correction_segments[index]
	img = open_image(img)

	print "Fetching new brush"
	paint_routine.getBrush(index)

	print "Recomposition"
	recomposer = iterativeErosionRecomposer(img, [3])
	LLT = recomposer.recompose()

	print "LLT to Paint: ", LLT
	testLLT(LLT,3)

	print "Let's Paint a Picture ~"
	paint_routine.Paint(LLT)

	print "LLT Finished "

paint_routine.returnToStart()
print "Routine Complete, Enjoy ! "


paint_routine.moveGantry(-50, 0)

img = cam.read_camera()
util.save(img, "06_camera_read_final")

dewarp_img = cam.dewarp(img)
a, w, h = dewarp_img.shape
dewarp_img = dewarp_img[70:w-250, 170:h-170]
util.save(img, "07_dewarp_camera_read_final")

