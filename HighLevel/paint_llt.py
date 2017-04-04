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
if not could_connect : 
	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)

##################################################################
######################## PAINT ROUTINE ###########################
##################################################################
# Gantry should start over paper's (0,0)
# Get Orders to paint
orders_to_paint = "./resources/orders/music_orders2.txt"

# Convert Orders to LLT
LLT = loadLLT(orders_to_paint)
testLLT(LLT,3)

# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)

# Paint Routine
print "Fetching new brush"
paint_routine.getBrush(0)

print "Let's Paint a Picture ~"
paint_routine.Paint(LLT)

paint_routine.returnToStart()
print "Routine Complete, Enjoy !"










