#! /usr/bin/env python
# MQP -- CARP Project
#
# This script takes an input image and 
# paints it with the robot with the current
# Arduino low level

# Import dependencies
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
from decomposition.grayscale_segmentation.grayscale_segmentation import *
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *
from common.util import *
from time import sleep
import cv2

##################################################################
##########################  SETUP  ###############################
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
if not could_connect : 
	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)

##################################################################
###################### PREPROCESSING  ############################
##################################################################
print "Preprocessing"

# take in image to process
input_image = 'resources/images/input/grayscale_test.png'

desiredImg = cv2.imread(input_image, cv2.IMREAD_COLOR)

##################################################################
################### DECOMPOSITION  ###############################
##################################################################
print "Decomposition"
image_root, image_set = grayscale_segment(desiredImg, 3)

##################################################################
############ RECOMPOSITION & PAINT ROUTINE  ######################
##################################################################

# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)

for img in image_set:
	display(img)

	# Binarize img first
	gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	(thresh, binImg) = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

	display(binImg)

	# Create a recomposer
	print "Recomposition"
	# recomposer = iterativeErosionRecomposer(binImg, [2])
	recomposer = skeletonRecomposer(binImg, [])

	LLT = recomposer.recompose()

	print "LLT ", LLT

	testLLT(LLT,3)

	print "Let's Paint a Picture ~"
	paint_routine.Paint(llt)

	print "LLT Finished "


print "Routine Complete, Enjoy ! "



	























