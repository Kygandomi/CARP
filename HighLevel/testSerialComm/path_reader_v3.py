#! /usr/bin/env python
# MQP -- CARP Project
# Path Reader V2 Code

import math
import serial_communication as ser_comm
from time import sleep

def send_standard_packet(packet):
	# Send a packet
	# print "sending : "+str(packet)
	arduino_ser.flush()
	arduino_ser.send_standard_packet(packet)
	# Wait a bit for Arduino to process point
	sleep(0.2)

def send_special_packet():
	# Tell Arduino to process all recieved packets
	arduino_ser.send_special_packet()
	arduino_ser.flush()

	# Wait for gantry routine to complete
	read_val = arduino_ser.recieve_packet()
	parse_val = arduino_ser.parse_packet(read_val)
	print "***** SENDING SPECIAL PACKET *****"
	print "init read : " + str(read_val) + " => " + str(parse_val)
	while( parse_val != 0):
		read_val = arduino_ser.recieve_packet()
		parse_val = arduino_ser.parse_packet(read_val)
		# print "read : " + str(read_val) + " => " + str(parse_val)
		sleep(0.1)
	print "Motion Complete!"

# file to read from 
fname = "../test_ImageRecomposition/orders/orders_rocket.txt"

baud = 115200
ports_list = ['COM3', '/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9']

for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if(arduino_ser.connect()):
		break

# Sleep to verify a solid connection
sleep(1)

# Is first element? 
first_elem = True

# Open the given file
with open(fname) as f:
	# For each line in the file
	for line in f:
		# print "Next Line"
		# Get the coordinates
		if(line == '\n'):
			print "Line Break"
			firgelli_up = [0, 0, 0, 400, 1, 800]

			# Send Firgelli Up packet
			send_standard_packet(firgelli_up)

			# Send commands and wait 
			send_special_packet()

			# Sleep for a second for the firgelli
			sleep(1)

			# Reset the first element flag
			first_elem = True
			
		# Do stuff	
		else:
			print "Sending Line"
			coords = line.split(" ")

			element = [int(float(coords[0]) * 10), int(float(coords[1]) * 10), 1, 0, 0, 800]
			send_standard_packet(element)

			if(first_elem):
				print "First Element"
				first_elem = False
				
				firgelli_down = [int(float(coords[0]) * 10), int(float(coords[1]) * 10), 1, 175, 1, 800]
				send_standard_packet(firgelli_down)
				
				# Send commands and wait 
				send_special_packet()

				# Sleep for a second for the firgelli
				sleep(1)



