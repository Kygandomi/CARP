#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V2 Code


import math
import serial_communication as ser_comm
from time import sleep

def send_commands(packet):
	arduino_ser.send_long_packet(packet)

	# Wait for gantry routine to complete
	read_val = arduino_ser.recieve_packet()
	print "READ VALUE WAS : " + str(read_val)
	while(arduino_ser.parse_packet(read_val) != -1):
		read_val = arduino_ser.recieve_packet()
		sleep(1)

# file to read from 
fname = "../test_ImageRecomposition/erosion/orders_cat.txt"

# Connect to Arduino over serial
baud = 115200
port = '/dev/tty.usbmodem1411'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

# Sleep to verify a solid connection
sleep(1)

# Commands
commands = []

# Is first element? 
first_elem = True

# Open the given file
with open(fname) as f:
	# For each line in the file
	for line in f:

		# Get the coordinates
		if(line == '\n'):
			fergelli_up = [0, 0, 0, 400, 1, 800]
			commands.append(fergelli_up)
			
			# Send commands and wait 
			print "Newline Commands"
			send_commands(commands)

			# Sleep for a second for the fergelli
			sleep(1)

			first_elem = True
			
		# Do stuff	
		else:
			print "In here"
			coords = line.split(" ")
			element = [int(float(coords[0]) * 10.9), int(float(coords[1]) * 10.9), 1, 0, 0, 800]
			commands.append(element)

			if(first_elem):
				print "First Element"
				first_elem = False
				fergelli_down = [int(float(coords[0]) * 10.9), int(float(coords[1]) * 10.9), 1, 175, 1, 800]
				commands.append(fergelli_down)
				
				# Send commands and wait 
				send_commands(commands)

				# Sleep for a second for the fergelli
				sleep(1)

				# Clear Commands
				commands = []



