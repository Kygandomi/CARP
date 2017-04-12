#! /usr/bin/env python
# MQP -- CARP Project
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *

from decomposition.decomp_color.decomp_color import *
from paint_with_pmd import ethernet_communication as eth_comm

from camera.CanvasCamera import Camera
from camera.CameraException import *

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

def gaussian_LLT(mu_x, sigma_x, mu_y, sigma_y, num_points):
	# Create Randomly distributed LLT
	print "Creating Distribution for LLT"
	out_pts = []
	list_pts=[]

	out_pts_scaled = []
	list_pts_scaled = []
	for i in range(0, num_points):
	    
	    x1 = abs(np.random.normal(mu_x, sigma_x, 1)[0])
	    y1 = abs(np.random.normal(mu_y, sigma_y, 1)[0])

	    list_pts.append([x1, y1])
	    list_pts_scaled.append([x1*10, y1*10])
	out_pts.append(list_pts)
	out_pts_scaled.append(list_pts_scaled)

	LLT = out_pts
	print LLT

	LLT_scaled = out_pts_scaled
	print LLT_scaled

	testLLT(LLT,3)

	return LLT_scaled


##################################################################
######################## PAINT ROUTINE ###########################
##################################################################
# Lets Paint
com_obj = setup_communications_eth()
paint_routine = PaintOrders.paint_orders(com_obj)

# Variables for the distribution
(img_width, img_height) = (8.5*25.4, 11*25.4)
mu_x, sigma_x = img_width/1.5, 30
mu_y, sigma_y = img_height/3, 30

num_points = 100
number_of_colors = 3

for i in range(number_of_colors):
	gauss_LLT = gaussian_LLT(mu_x, sigma_x, mu_y, sigma_y)

	print "Fetching new brush"
	paint_routine.getBrush(i)

	print "Painting LLT..."
	paint_routine.Paint(gauss_LLT)

	print "LLT completed"

print "Routine Complete"
paint_routine.returnToStart()

