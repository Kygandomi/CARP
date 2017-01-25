#! /usr/bin/env python
# MQP -- CARP Project
#
# This script takes an input image and 
# paints it with the robot with the current
# Arduino low level

# Import dependencies
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders
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
input_image = 'resources/images/input/pig.png'

desiredImg = cv2.imread(input_image, cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)


##################################################################
################### DECOMPOSITION  ###############################
##################################################################
# print "Decomposition"

##################################################################
################### RECOMPOSITION  ###############################
##################################################################
print "Recomposition"

# Create a recomposer
recomposer = skeletonRecomposer(desiredImg_grey, [])

LLT = recomposer.recompose()

print "LLT ", LLT

# testLLT(LLT,3)

##################################################################
####################  PAINTING ROUTINE  ##########################
##################################################################
print "Let's Paint a Picture ~"

# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)
paint_routine.Paint(LLT)





















