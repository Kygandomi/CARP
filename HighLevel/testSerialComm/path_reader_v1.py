#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V1 Class

# Useful Conversions:
# 10.9 from mm to steps
# 8.5 in x 11 in 
# 36.6938022 mm per rotation 


import math
import serial_communication as ser_comm
from time import sleep

def forward_kinematics(desired_x, desired_y):
	m1_dir = 0
	m2_dir = 0

	# x = desired_y
	# y = desired_x

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
fname = "catordersSmallBrush3.txt"

# Connect to Arduino over serial
baud = 115200
port = '/dev/tty.usbmodem1411'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

# Sleep to verify a solid connection
sleep(1)

# Set step time for motors in microseconds
step_time = 800 
prev_was_new_line = False
fergelli_pos = 168

# keep track of location
current_x = 0
current_y = 0

mm_to_step = 10.9
count = 0

# Read in each line of 
with open(fname) as f:
	for line in f:

		coords = line.split(" ")

		# Get desired x and y
		x1 = float(coords[0]) * mm_to_step
		y1 = float(coords[1]) * mm_to_step

		# Get Change in pos
		delta_x1 = x1 - current_x
		delta_y1 = y1 - current_y

		# Verify that the data is valid
		upper_bound_x = 250*mm_to_step
		upper_bound_y = 420*mm_to_step

		if(x1 > upper_bound_x or y1 > upper_bound_y ):
			print "Coordinate too Large"
		elif(x1 < 0 or y1 < 0 ):
			print "Coordinate too Small"

		# Else we're all set
		else :
			# Get motor steps and direction
			m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x1, delta_y1)

			print "*************"
			print count
			print current_x 
			print current_y
			print m1_steps
			print m2_steps
			print x1 
			print y1
			count += 1

			# Move the gantry
			print "move gantry"
			arduino_ser.send_packet(m1_dir, m1_steps, step_time, m2_dir, m2_steps, step_time, 300)

			# Wait for gantry routine to complete
			read_val = arduino_ser.recieve_packet()
			while(arduino_ser.parse_packet(read_val) != -1):
				read_val = arduino_ser.recieve_packet()
				sleep(1)

			# Set Fergelli Down
			arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, 170)

			# Let's just wait for the fergelli to finish its routine
			sleep(2)

			# Lift the fergelli up
			arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, 300)

			# Let's just wait for the fergelli to finish its routine
			sleep(2)

			# if prev_was_new_line : 
			# 	# Lower Fergelli for next contour
			# 	print "fergelli down"
			# 	arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, 168)

			# 	# Let's just wait for the fergelli to finish its routine
			# 	sleep(2)

			# 	fergelli_pos = 168
			# 	prev_was_new_line = False


			# Reset prev pos
			current_x = x1
			current_y = y1

			print "repeat"

# text_file.close()
print "END"

# Move fergelli down
				
# Move fergelli up
				





