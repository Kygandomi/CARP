#! /usr/bin/env python
# MQP -- CARP Project
# Ethernet Class -- Handles Communication to PMD

from struct import pack,unpack
import socket   

'''This class handles TCP/IP communication with PMD'''
class ethernet_comms():

	'Constructor for serial class, sets up serial comms'
	def __init__(self, ip, port):
		# IP and Port to be used
		self.ip = ip
		self.port = port
		self.eth = ''
		self.buff_size = 1024

	'Connects to PMD over Ethernet'
	def connect(self):
		# Open Serial Port if possible
		try :
		# Connect to serial port
			self.eth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.eth.connect((self.ip, self.port))
			self.eth.settimeout(1)
			#(name, aliaslist, ipaddrlist) = socket.gethostbyaddr(self.ip )
			#print(name + ' is open...')
			return True
		except:
		 	print "failed to connect"
			return False

	'Disconnects PMD'
	def disconnect(self):
		self.eth.close()

	'Clears input and output buffers ?'
	def flush(self):
		pass

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

		self.eth.send(pack('c4h2c',b'\xfe',x,y,z,min_step_time,mask,b'\xef'))

		# self.eth.send(b'\xfe')

		# self.eth.send(('%%0%dx' % (length << 1) % x).decode('hex')[-length:])
		# self.eth.send(('%%0%dx' % (length << 1) % y).decode('hex')[-length:])
		# self.eth.send(('%%0%dx' % (length << 1) % z).decode('hex')[-length:])
		# self.eth.send(('%%0%dx' % (length << 1) % min_step_time).decode('hex')[-length:])

		# self.eth.send(mask)
		
		# self.eth.send(b'\xef')

	'Read data from the PCB'
	def recieve_packet(self):
		# Collect output response
		try:
			response_data = self.eth.recv(self.buff_size)
			print 'response: ',repr(response_data)
			if len(response_data)>0:
				return unpack('B4h2B',response_data)
			return []
		except:
			print "err: timeout"
			return []
		#return unpack(str(len(response_data))+'B',response_data)

	'Parse recieved data'
	def parse_packet(self, response_data):
		if(len(response_data) >= 3):
			for i in range(len(response_data)):
				if(response_data[i] == 239):
					return response_data[i-1]
		else :
			return -1




