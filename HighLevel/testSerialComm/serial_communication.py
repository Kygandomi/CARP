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
	def connect(self ):
		# Open Serial Port if possible
		try :
			# Connect to serial port
			self.ser = serial.Serial(self.port, self.baud)
			if self.ser.isOpen(): 
				print(self.ser.name + ' is open...')
				return True
		except:
			return False

	'Closes serial port to Arduino'
	def disconnect(self):
		self.ser.close()

	def flush(self):
		self.ser.flushInput()
		self.ser.flushOutput()

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

	def send_standard_packet(self, element):

		length = 2

		x = element[0]
		y = element[1]
		z = element[2]

		min_step_time = element[3]

		xy_abs_flag = element[4]
		z_abs_flag = element[5]
		go_flag = element[6]

		mask = chr((z_abs_flag<<2)|(xy_abs_flag<<1)|go_flag)

		self.ser.write(b'\xfe')

		self.ser.write(('%%0%dx' % (length << 1) % x).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % y).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % z).decode('hex')[-length:])
		self.ser.write(('%%0%dx' % (length << 1) % min_step_time).decode('hex')[-length:])
		self.ser.write(mask)
		
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
			for i in range(len(response)):
				if(response[i] == 239):
					return response[i-1]
		else :
			return -1






