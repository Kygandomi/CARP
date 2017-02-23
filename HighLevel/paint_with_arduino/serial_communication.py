#! /usr/bin/env python
# MQP -- CARP Project
# Serial Class -- Handles Communication to Arduino

import serial
from struct import pack,unpack
import threading
from time import sleep

'''This class handles serial communication with pcb'''
class serial_comms():

	'Constructor for serial class, sets up serial comms'
	def __init__(self, port, baud):
		# Port and Baud Rate to be used
		self.port = port
		self.baud = baud
		self.ser = ''
		self.clearThread = threading.Thread(target=self.clearBuffer)

	def clearBuffer(self):
		while True:
			self.ser.flushInput()
			sleep(30)

	'Connects to Arduino over serial'
	def connect(self):
		# Open Serial Port if possible
		try :
			# Connect to serial port
			self.ser = serial.Serial(self.port, self.baud)
			if self.ser.isOpen(): 
				print(self.ser.name + ' is open...')
				self.clearThread.start()
				return True
		except:
			return False

	'Closes serial port to Arduino'
	def disconnect(self):
		self.ser.close()

	'Clears input and output serial buffers'
	def flush(self):
		self.ser.flushInput()
		self.ser.flushOutput()

	'Sends a "standard" packet to the robot'
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

		self.ser.write(pack('c4h2c',b'\xfe',x,y,z,min_step_time,mask,b'\xef'))

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






