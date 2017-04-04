#! /usr/bin/env python
# MQP -- CARP Project
from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *

from decomposition.decomp_color.decomp_color import *

from camera.CanvasCamera import Camera
from camera.CameraException import *

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

##################################################################
######################## PAINT ROUTINE ###########################
##################################################################
# Lets Paint
paint_routine = PaintOrders.paint_orders(arduino_ser)

# Variables for the distribution
(img_width, img_height) = (8.5*25.4, 11*25.4)
mu_x, sigma_x = img_width/1.5, 30
mu_y, sigma_y = img_height/3, 30
num_points = 50

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

print "Fetching new brush"
paint_routine.getBrush(0)

print "Painting LLT..."
paint_routine.Paint(LLT_scaled, up_val=250, paint_distance=1300)

print "Routine Complete"
paint_routine.returnToStart()
















