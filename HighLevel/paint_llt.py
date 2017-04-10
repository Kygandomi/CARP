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

##################################################################
##########################  SETUP  ###############################
##################################################################
print "Setup"

print "Connecting to Controller..."
com_obj = setup_communications_eth()
paint_routine = PaintOrders.paint_orders(com_obj)

##################################################################
######################## PAINT ROUTINE ###########################
##################################################################
# Gantry should start over paper's (0,0)
# Get Orders to paint

orders_to_paint = "./resources/orders/latestLLT.txt"
# Convert Orders to LLT
LLT = loadLLT(orders_to_paint)
if len(LLT)==0:
	raise Exception('Error: File "'+orders_to_paint+'" is empty or missing')
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










