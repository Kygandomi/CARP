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
from decomposition.decomp_color.decomp_color import *
from recomposition.skeleton.skeletonRecompose import *
from common.util import *
from common import color_pallete
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
desiredImg = readImage("star_flower.png", type_flag=1)

##################################################################
################### DECOMPOSITION  ###############################
##################################################################
print "Decomposition"

<<<<<<< HEAD
segmented_image, [colors,color_segments], [canvas,canvas_segment]  = decompose(desiredImg, 6,[], color_pallete.white)

display(desiredImg)
display(segmented_image)
for index in range(len(color_segments)):
	display(color_segments[index],str(colors[index]))
=======
blue = [255,0,0]
green = [0,255,0]
yellow = [154,233,255]
red = [0,0,255]
white = [255,255,255]
black = [0,0,0]

print "Quantization"
colors = color_quantize(desiredImg,4)
colors = remove_canvas(colors,white)
#colors = classify(colors,[blue,green,yellow,red,black])

print "Segmentation"
segmented_image, color_segments, canvas_segment  = color_segment(desiredImg, colors, white)

for image in color_segments:
	img4 = open_image(image)
	display(img4)
>>>>>>> origin/master

##################################################################
############ RECOMPOSITION & PAINT ROUTINE ######################
##################################################################

# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)

# Recomposers to use
recompItErosion1 = iterativeErosionRecomposer(open_image(color_segments[0]), [3])
recompItErosion2 = iterativeErosionRecomposer(open_image(color_segments[1]), [2])
recompSkeleton = skeletonRecomposer(open_image(color_segments[2]), [])
recomposers = [recompItErosion1, recompItErosion2, recompSkeleton]

# Recomp and Paint
for index in range(len(color_segments)):
<<<<<<< HEAD
    print "Index: ", index
    img = color_segments[index]
    
    print "Recomposition"
    recomposer = iterativeErosionRecomposer(img, [3])
    # recomposer = skeletonRecomposer(img, [])
    LLT = recomposer.recompose()
    testLLT(LLT,3)

    print "Fetching new brush"
    paint_routine.getBrush(index)

    print "Let's Paint a Picture ~"
    paint_routine.Paint(LLT, index)

    print "LLT Finished "
=======
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
>>>>>>> origin/master
	
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























