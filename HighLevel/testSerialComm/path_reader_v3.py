#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V3 Code

# Import dependencies
import math
import serial_communication as ser_comm
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
		print "init read : " + str(read_val) + " => " + str(parse_val)
		while( parse_val != 0):
			read_val = arduino_ser.recieve_packet()
			parse_val = arduino_ser.parse_packet(read_val)
			sleep(0.1)
		print "Motion Complete!"

		# Sleep for a bit for the firgelli
		sleep(4)



##################################################################
############################## MAIN ##############################
##################################################################

# file to read from 
fname = "../test_ImageRecomposition/orders/orders_coffee.txt"

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

# Open the given file
with open(fname) as f:
	# For each line in the file
	for line in f:
		# Get the coordinates
		if(line == '\n'):
			# Print for debugging
			print "Line Break"

			# Fergelli Up Routine
			firgelli_up = [0, 0, 400, 800, 0, 1, 1]

			# Send Firgelli Up packet and Execute List of Commands
			send_standard_packet(firgelli_up)

			# Reset the first element flag
			first_elem = True
			
		# Do stuff	
		else:
			print "Sending Line"

			# Get coords to send
			coords = line.split(" ")

			# Create packet to send
			element = [int(float(coords[0]) * 10), int(float(coords[1]) * 10), 0, 800, 1, 0, 0]
			send_standard_packet(element)

			if(first_elem):
				print "First Element"
				first_elem = False
				
				firgelli_down = [0, 0, 170, 800, 0, 1, 1]
				send_standard_packet(firgelli_down)



