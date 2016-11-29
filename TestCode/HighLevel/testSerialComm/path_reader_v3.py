#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V3 Code

# Import dependencies
import math
import serial_communication as ser_comm
import random
from time import sleep

# Routine for sending a standard packet via Serial 
def send_standard_packet(packet):
	# Send a packet
	arduino_ser.flush()
	arduino_ser.send_standard_packet(packet)


	# Check the go flag
	if(packet[6] == 0):
		# Wait a bit for Arduino to process point
		sleep(0.2)


	# Check the go flag
	elif(packet[6] == 1):
		# Wait for gantry routine to complete
		read_val = arduino_ser.recieve_packet()
		parse_val = arduino_ser.parse_packet(read_val)
		print "***** SENDING SPECIAL PACKET *****"
		# print "init read : " + str(read_val) + " => " + str(parse_val)
		while( parse_val != 0):
			read_val = arduino_ser.recieve_packet()
			parse_val = arduino_ser.parse_packet(read_val)
			sleep(0.1)
		print "Motion Complete!"

		# Sleep for a bit for the firgelli
		sleep(2)

def getPaint():
	# Get Paint Routine
	firgelli_up = [0, 0, 600, 800, 0, 1, 1]
	send_standard_packet(firgelli_up)

	element = [random.randint(0,25), random.randint(0,25), 0, 800, 1, 0, 0]
	send_standard_packet(element)

	firgelli_down = [0, 0, 175, 800, 0, 1, 1]
	send_standard_packet(firgelli_down)

	firgelli_up = [0, 0, 600, 800, 0, 1, 1]
	send_standard_packet(firgelli_up)


##################################################################
############################## MAIN ##############################
##################################################################

# file to read from 
fname = "../test_ImageRecomposition/orders/orders_rocket.txt"

# Establish Serial Connection
baud = 115200
ports_list = ['COM3', '/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9']
for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if(arduino_ser.connect()):
		break

# Sleep to verify a solid connection
sleep(1)

# Is this the first element? 
first_elem = True

# Record how far we've gone
MAX_DIST = 2000
paint_distance = MAX_DIST

# Save previous position
prev_dx = 0
prev_dy = 0

strokes = []
stroke_i = 0
point_i = 0

# Read in all points from file
with open(fname) as f:
	# For each line in the file
	stroke = []
	for line in f:
		if(line == '\n'):
			strokes.append(stroke)
			stroke = []
		else:
			coords = line.split(" ")

			# Create packet to send
			dx = int(float(coords[0]) * 10)
			dy = int(float(coords[1]) * 10)

			stroke.append((dx,dy))


while stroke_i<len(strokes):
	while point_i < len(strokes[stroke_i]):
		if(paint_distance >= MAX_DIST):
			getPaint()
			point_i = max(0,point_i-3)
			first_elem = True
			paint_distance = 0

		dx = strokes[stroke_i][point_i][0]
		dy = strokes[stroke_i][point_i][1]

		element = [dx, dy, 0, 800, 1, 0, 0]
		send_standard_packet(element)

		# Increase Paint Distance
		if not first_elem:
			paint_distance += math.sqrt((dx-strokes[stroke_i][max(0,point_i-1)][0])**2 + (dy-strokes[stroke_i][max(0,point_i-1)][1])**2)
			print paint_distance
		else:
			print "First Element"
			first_elem = False
			
			firgelli_down = [0, 0, 170, 800, 0, 1, 1]
			send_standard_packet(firgelli_down)

		point_i += 1

	# Done with current stroke
	firgelli_up = [0, 0, 600, 800, 0, 1, 1]
	send_standard_packet(firgelli_up)
	first_elem = True
	point_i=0
	stroke_i += 1
	if(MAX_DIST-paint_distance < 300)
		paint_distance = MAX_DIST

firgelli_up = [0, 0, 600, 800, 0, 1, 1]
send_standard_packet(firgelli_up)

element = [0, 0, 0, 800, 1, 0, 0]
send_standard_packet(element)


# # Open the given file
# with open(fname) as f:
# 	# For each line in the file
# 	for line in f:
# 		if(paint_distance >= 2000):
# 			# Get Paint Routine
# 			firgelli_up = [0, 0, 600, 800, 0, 1, 1]
# 			send_standard_packet(firgelli_up)

# 			element = [random.randint(0,25), random.randint(0,25), 0, 800, 1, 0, 0]
# 			send_standard_packet(element)

# 			firgelli_down = [0, 0, 175, 800, 0, 1, 1]
# 			send_standard_packet(firgelli_down)

# 			firgelli_up = [0, 0, 600, 800, 0, 1, 1]
# 			send_standard_packet(firgelli_up)

# 			# Reset First Element
# 			first_elem = True
# 			paint_distance = 0

# 		# Get the coordinates
# 		if(line == '\n'):
# 			# Print for debugging
# 			print "Line Break"

# 			# Fergelli Up Routine
# 			firgelli_up = [0, 0, 600, 800, 0, 1, 1]

# 			# Send Firgelli Up packet and Execute List of Commands
# 			send_standard_packet(firgelli_up)

# 			# Reset the first element flag
# 			first_elem = True
			
# 		# Do stuff	
# 		else:
# 			print "Sending Line"

# 			# Get coords to send
# 			coords = line.split(" ")

# 			# Create packet to send
# 			dx = int(float(coords[0]) * 10)
# 			dy = int(float(coords[1]) * 10)

# 			element = [dx, dy, 0, 800, 1, 0, 0]
# 			send_standard_packet(element)

# 			# Increase Paint Distance
# 			if(not first_elem):
# 				paint_distance += math.sqrt((dx-prev_dx)**2 + (dy-prev_dy)**2)
# 				print paint_distance

# 			if(first_elem):
# 				print "First Element"
# 				first_elem = False
				
# 				firgelli_down = [0, 0, 170, 800, 0, 1, 1]
# 				send_standard_packet(firgelli_down)

# 			prev_dx = dx
# 			prev_dy = dy



