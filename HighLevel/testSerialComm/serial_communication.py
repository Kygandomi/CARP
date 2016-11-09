#! /usr/bin/env python
# MQP -- CARP Project
# Serial Class -- Handles Communication to Arduino

import serial

'This class handles serial communication with pcb'
class serial_comms():

	'Constructor for serial class, sets up serial comms'
	def __init__(self, port, baud):
		# Port and Baud Rate to be used
		self.port = port
		self.baud = baud
		self.ser = ''

	'Connects to Arduino over serial'
	def connect(self):
		 # Connect to serial port
		self.ser = serial.Serial(self.port, self.baud)

		# Open Serial Port if possible
		if self.ser.isOpen() : 
			print(self.ser.name + ' is open...')

	'Closes serial port to Arduino'
	def disconnect(self):
		self.ser.close()

	'Write data to the Arduino'
	def send_packet(self, m1_dir, m1_step, m1_step_time, 
						  m2_dir, m2_step, m2_step_time,
						  fergelli_pos):

		length = 2
		# Write Command to Arduino
		self.ser.write(b'\xfe')
		self.ser.write(chr(m1_dir))
		self.ser.write(('%%0%dx' % (length << 1) % m1_step).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % m1_step_time).decode('hex')[-length:])

		self.ser.write(chr(m2_dir))
		self.ser.write(('%%0%dx' % (length << 1) % m2_step).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % m2_step_time).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % fergelli_pos).decode('hex')[-length:])
		self.ser.write(b'\xef')

	def send_long_packet(self, packet):
		length = 2
		self.ser.write(b'\xfe')

		for element in packet:
			x = element[0]
			y = element[1]
			xy_abs_flag = element[2]
			z = element[3]
			z_abs_flag = element[4]
			min_step_time = element[5]

			self.ser.write(('%%0%dx' % (length << 1) % x).decode('hex')[-length:])
			self.ser.write(('%%0%dx' % (length << 1) % y).decode('hex')[-length:])
			self.ser.write(chr(xy_abs_flag))
			self.ser.write(('%%0%dx' % (length << 1) % z).decode('hex')[-length:])
			self.ser.write(chr(z_abs_flag))
			self.ser.write(('%%0%dx' % (length << 1) % min_step_time).decode('hex')[-length:])
		
		self.ser.write(b'\xef')

	'Read data from the PCB'
	def recieve_packet(self):
		# Collect output response
		response = []
		while (self.ser.inWaiting()):
			output = ord(self.ser.read())
			response.append(output)

		return response

	'Parse recieved data'
	def parse_packet(self, response):
		if(len(response) >= 3):
			return response[1]
		else :
			return -1






