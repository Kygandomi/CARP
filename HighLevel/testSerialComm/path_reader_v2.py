#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V2 Code


# Useful Conversions:
# 10.9 from mm to steps
# 8.5 in x 11 in 
# 36.6938022 mm per rotation


import math
import serial_communication as ser_comm
from time import sleep

################## METHODS ##################
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

def gantry_movement_routine(m1_steps, m2_steps, m1_dir, m2_dir, step_time, fergelli_pos):
	# Move the gantry
	print "Moving the Gantry"
	arduino_ser.send_packet(m1_dir, m1_steps, step_time, m2_dir, m2_steps, step_time, fergelli_pos)

	# Wait for gantry routine to complete
	read_val = arduino_ser.recieve_packet()
	while(arduino_ser.parse_packet(read_val) != -1):
		read_val = arduino_ser.recieve_packet()
		sleep(1)

def fergelli_down(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_down_dist):
	# Move the Fergelli Down
	print "Moving Fergelli Down"
	arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, fergelli_down_dist)

	# Let's just wait for the fergelli to finish its routine
	sleep(fergelli_delay)

def fergelli_up(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_up_dist):
	# Move the Fergelli Up
	print "Moving Fergelli Up"
	arduino_ser.send_packet(m1_dir, 0, step_time, m2_dir, 0, step_time, fergelli_up_dist)

	# Let's just wait for the fergelli to finish its routine
	sleep(fergelli_delay)

def paint_points(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist):
	# Get desired x and y
	x1 = float(coords[0]) * mm_to_step
	y1 = float(coords[1]) * mm_to_step

	# Get Change in pos
	delta_x1 = x1 - current_x
	delta_y1 = y1 - current_y

	# Verify that the data is valid
	if(x1 > upper_bound_x or y1 > upper_bound_y ):
		print "Error: Coordinate too Large"
	elif(x1 < 0 or y1 < 0 ):
		print "Error: Coordinate too Small"

	# Given that the data is valid
	else :
		# Get motor steps and direction
		m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x1, delta_y1)

		# Move the gantry
		gantry_movement_routine(m1_steps, m2_steps, m1_dir, m2_dir, step_time, fergelli_up_dist)

		# Move the Fergelli Down
		fergelli_down(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_down_dist)

		# Move the Fergelli Up
		fergelli_up(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_up_dist)

	# Return the new current position
	return x1, y1

def paint_lines(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist):
	# Get desired x and y
	x1 = float(coords[0]) * mm_to_step
	y1 = float(coords[1]) * mm_to_step

	x2 = float(coords[2]) * mm_to_step
	y2 = float(coords[3]) * mm_to_step

	# Get Change in pos
	delta_x1 = x1 - current_x
	delta_y1 = y1 - current_y

	delta_x2 = x2 - x1
	delta_y2 = y2 - x2

	# Verify that the data is valid
	if(x1 > upper_bound_x or y1 > upper_bound_y or x2 > upper_bound_x or y2 > upper_bound_y ):
		print "Error: Coordinate too Large"
	elif(x1 < 0 or y1 < 0 ):
		print "Error: Coordinate too Small"

	# Given that the data is valid
	else :
		# Get motor steps and direction
		m1_steps_1, m2_steps_1, m1_dir_1, m2_dir_1 = forward_kinematics(delta_x1, delta_y1)
		m1_steps_2, m2_steps_2, m1_dir_2, m2_dir_2 = forward_kinematics(delta_x2, delta_y2)

		print str(m1_steps_1) + " " + str(m2_steps_1) + " " + str(m1_steps_2) + " "+ str(m2_steps_2)

		# Move the gantry
		gantry_movement_routine(m1_steps_1, m2_steps_1, m1_dir_1, m2_dir_1, step_time, fergelli_up_dist)

		# Move the Fergelli Down
		fergelli_down(m1_dir_1, m2_dir_1, step_time, fergelli_delay, fergelli_down_dist)

		# Move the gantry
		gantry_movement_routine(m1_steps_2, m2_steps_2, m1_dir_2, m2_dir_2, step_time, fergelli_down_dist)

		# Move the Fergelli Up
		fergelli_up(m1_dir_2, m2_dir_2, step_time,fergelli_delay, fergelli_up_dist)

		# Return the new current position
		return x2, y2

def paint_contours(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist, contour_flag, prev_contour_flag):
	# If the contour flag has been signalled
	if(contour_flag):
		# Move the Fergelli Up
		m1_dir = 0
		m2_dir = 0
		fergelli_up(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_up_dist)
		
		contour_flag = False
		prev_contour_flag = True
		x1 = current_x
		y1 = current_y

	# Else the contour flag has not been signaled 
	else:
		# Get desired x and y
		x1 = float(coords[0]) * mm_to_step
		y1 = float(coords[1]) * mm_to_step

		# Get Change in pos
		delta_x1 = x1 - current_x
		delta_y1 = y1 - current_y

		# Verify that the data is valid
		if(x1 > upper_bound_x or y1 > upper_bound_y ):
			print "Error: Coordinate too Large"
		elif(x1 < 0 or y1 < 0 ):
			print "Error: Coordinate too Small"

		# If the last point was the contour flag
		if(prev_contour_flag):
			# Get motor steps and direction
			m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x1, delta_y1)

			# Move the gantry
			gantry_movement_routine(m1_steps, m2_steps, m1_dir, m2_dir, step_time, fergelli_up_dist)

			# Move the Fergelli Down
			m1_dir = 0
			m2_dir = 0
			fergelli_down(m1_dir, m2_dir, step_time, fergelli_delay, fergelli_down_dist)
			contour_flag = False
			prev_contour_flag = False

		else:
			# Get motor steps and direction
			m1_steps, m2_steps, m1_dir, m2_dir = forward_kinematics(delta_x1, delta_y1)

			# Move the gantry
			gantry_movement_routine(m1_steps, m2_steps, m1_dir, m2_dir, step_time, fergelli_down_dist)
			contour_flag = False
			prev_contour_flag = False

	return x1, y1, contour_flag, prev_contour_flag


####################### MAIN #########################

# file to read from 
fname = "../test_ImageRecomposition/fill/HorFillOrders.txt"

# Connect to Arduino over serial
baud = 115200
port = 'COM8'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

# Sleep to verify a solid connection
sleep(1)

# Conversions of Value
mm_to_step = 10.9

# Set step time for motors in microseconds
step_time = 800 

# Get bounds for data
upper_bound_x = 250*mm_to_step
upper_bound_y = 420*mm_to_step

# Contour Flag
contour_flag = False
prev_contour_flag = False

# Fergelli setpoints
fergelli_delay = 3
fergelli_up_dist = 350
fergelli_down_dist = 170

# keep track of location
current_x = 0
current_y = 0

# keep track of the line we're one
line_counter = 0

# Painting mode
mode = 'lines'

# Open the given file
with open(fname) as f:
	# For each line in the file
	for line in f:

		# Get the coordinates
		if(line == '\n'):
			contour_flag = True
			coords = [0, 0]
		else:
			coords = line.split(" ")
			contour_flag = False

		# Perform the action for the valid mode
		print "******"
		if(mode == 'points'):
			x, y = paint_points(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist)
		elif(mode == 'lines'):
			print "Lets make lines!"
			print str(coords)
			x, y = paint_lines(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist)
		elif(mode == 'contours'):
			x, y, f1, f2 = paint_contours(coords, mm_to_step, current_x, current_y, upper_bound_x, upper_bound_y, step_time, fergelli_delay, fergelli_up, fergelli_down_dist, contour_flag, prev_contour_flag)
			contour_flag = f1
			prev_contour_flag = f2
		else:
			print 'Error: Invalid Mode'
			break

		# Set current x and current y
		current_x = x
		current_y = y

		print x
		print y
		print line_counter
		line_counter += 1

print "Routine Finished ~"









