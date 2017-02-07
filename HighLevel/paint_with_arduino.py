#! /usr/bin/env python
# MQP -- CARP Project
#
# This script takes an input image and 
# paints it with the robot with the current
# Arduino low level

# Import dependencies
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from decomposition.color_segmentation.color_segmentation import *
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
# if not could_connect : 
# 	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)

###############################################################################################################
# WITH DECOMPOSITION !
##################################################################
###################### PREPROCESSING  ############################
##################################################################
print "Preprocessing"

# take in image to process
desiredImg = readImage("boat2.png", type_flag=1)

##################################################################
################### DECOMPOSITION  ###############################
##################################################################
print "Decomposition"

blue = [255,0,0]
green = [0,255,0]
yellow = [0,233,255]
red = [0,0,255]
white = [255,255,255]
black = [0,0,0]

segmented_image, color_segments, canvas_segment  = color_segment(desiredImg, [yellow, red, black],white)

for image in color_segments:
	display(image)

##################################################################
############ RECOMPOSITION & PAINT ROUTINE ######################
##################################################################

# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)

# Recomp and Paint
for index in range(len(color_segments)-1):
	print "Index ", index
	img = color_segments[index]

	print "Fetching new brush"
	paint_routine.getBrush(index)

	print "Recomposition"
	recomposer = iterativeErosionRecomposer(img, [3])
	# recomposer = skeletonRecomposer(img, [])

	LLT = recomposer.recompose()

	print "LLT to Paint: ", LLT
	testLLT(LLT,3)

	print "Let's Paint a Picture ~"
	paint_routine.Paint(LLT, index)

	print "LLT Finished "
	
paint_routine.returnToStart()
print "Routine Complete, Enjoy ! "

###############################################################################################################
# # WITHOUT DECOMPOSITION !
# ##################################################################
# ###################### PREPROCESSING  ############################
# ##################################################################
# print "Preprocessing"

# # take in image to process
# desiredImg = readImage("pikachu.png", type_flag=1)

# desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)

# (thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# ##################################################################
# ################### DECOMPOSITION  ###############################
# ##################################################################
# # print "Decomposition"

# ##################################################################
# ################### RECOMPOSITION  ###############################
# ##################################################################
# print "Recomposition"

# # Create a recomposer
# recomposer = skeletonRecomposer(binImg, [])
# # recomposer = iterativeErosionRecomposer(binImg, [4])

# LLT = recomposer.recompose()

# print "LLT ", LLT

# testLLT(LLT,3)

# ##################################################################
# ####################  PAINTING ROUTINE  ##########################
# ##################################################################
# print "Let's Paint a Picture ~"

# # Lets Paint
# paint_routine = PaintOrders.paint_orders(arduino_ser)
# paint_routine.Paint(LLT, -1)























