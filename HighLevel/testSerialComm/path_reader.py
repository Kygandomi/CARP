#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader Class

# Useful conversions: 
# 10.9 from mm to steps
# 8.5 in x 11 in 
# 36.6938022 mm per rotation 

import math
import serial_communication as ser_comm
from time import sleep
from copy import deepcopy

def forward_kinematics(desired_x, desired_y):
	m1_dir = 0
	m2_dir = 0

	mag = math.sqrt(math.pow(desired_x, 2) + math.pow(desired_y, 2))
	angle = math.atan2(desired_y, desired_x) 

	s1 = mag*math.sin(angle - 0.785398)
	s2 = mag*math.cos(angle - 0.785398)

	if(s1 < 0):
		m1_dir = 1
	else:
		m1_dir = 0

	if(s2 < 0):
		m2_dir = 1
	else:
		m2_dir = 0

	m1_steps = int(abs(s1))
	m2_steps = int(abs(s2))

	return m1_steps, m2_steps, m1_dir, m2_dir


#######################################################
####################   MAIN  ##########################
#######################################################

# file to read from 
fname = "orders2.txt"

# Connect to Arduino over serial
baud = 115200
port = '/dev/tty.usbmodem1411'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

sleep(1)

# Set step time for motors in microseconds
step_time = 800 

# keep track of location
current_x = 0
current_y = 0

mm_to_step = 10.9

# Read in each line of 
with open(fname) as f:
	for line in f:
		# Get coordinates
		coords = line.split(" ")

		# Get desired x and y
		x1 = float(coords[0]) * mm_to_step
		y1 = float(coords[1]) * mm_to_step

		x2 = float(coords[2]) * mm_to_step
		y2 = float(coords[3]) * mm_to_step

		delta_x1 = x1 - current_x
		delta_y1 = y1 - current_y

		delta_x2 = x2 - x1
		delta_y2 = y2 - y1

		# Verify that the data is valid
		upper_bound_x = 250*mm_to_step
		upper_bound_y = 420*mm_to_step

		if(x1 > upper_bound_x or y1 > upper_bound_y or x2 > upper_bound_x or y2 > upper_bound_y):
			print "Coordinate too Large"
		elif(x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0):
			print "Coordinate too Small"

		# Else we're all set
		else :
			######### First point of Line #############
			# Get motor steps and direction
			m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x1, delta_y1)

			# Move the gantry
			arduino_ser.send_packet(m1_dir, m1_steps, step_time, m2_dir, m2_steps, step_time, 700)

			# Wait for gantry routine to complete
			read_val = arduino_ser.recieve_packet()
			while(arduino_ser.parse_packet(read_val) != -1):
				read_val = arduino_ser.recieve_packet()
				sleep(1)

			# Move fergelli down
			arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, 175)

			# Let's just wait for the fergelli to finish its routine
			sleep(2)

			######### Second point of Line #############
			# Get motor steps and direction
			m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x2, delta_y2)

			# Move the gantry
			arduino_ser.send_packet(m1_dir, m1_steps, step_time, m2_dir, m2_steps, step_time, 175)

			# Wait for gantry routine to complete
			read_val = arduino_ser.recieve_packet()
			while(arduino_ser.parse_packet(read_val) != -1):
				read_val = arduino_ser.recieve_packet()
				sleep(1)

			# Move fergelli up
			arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, 700)

			# Let's just wait for the fergelli to finish its routine
			sleep(2)

			# Reset prev pos
			current_x = x2
			current_y = y2

print "END"

    




