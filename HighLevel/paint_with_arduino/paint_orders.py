#! /usr/bin/env python
# MQP -- CARP Project

# Import dependencies
import math
import random
import serial_communication as ser_comm
from time import sleep

'''This class handles painting routines with arduino low level'''
class paint_orders():

	'Constructor for paint orders class'
	def __init__(self, arduino_ser):
		# Save the ser com to use
		self.arduino_ser = arduino_ser

	'Routine for sending a standard packet via Serial' 
	def send_standard_packet(self, packet):
		# For our convenience a Standard Packet Consists of : 
		# [x,y,z, min_step_time, xy_abs_flag, z_abs_flag, go_flag] 

		# Send a standard packet to the arduino
		self.arduino_ser.flush()
		self.arduino_ser.send_standard_packet(packet)

		# Check the go flag -- not go time
		if(packet[6] == 0):
			# Wait a bit for Arduino to process point
			sleep(0.2)

		# Check the go flag -- its go time
		elif(packet[6] == 1):
			# Interpret incoming signals
			read_val = self.arduino_ser.recieve_packet()
			parse_val = self.arduino_ser.parse_packet(read_val)

			# While the gantry has not completed its motion routine
			while( parse_val != 0):
				# Interpret incoming signals
				read_val = self.arduino_ser.recieve_packet()
				parse_val = self.arduino_ser.parse_packet(read_val)
				sleep(0.1)
			print "Brush Stroke Motion Complete."

			# Sleep for a bit for the firgelli
			sleep(2)

	'Routine for reloading paint on the brush'
	def getPaint(self):
		# Get Paint Routine
		firgelli_up = [0, 0, 600, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)

		element = [random.randint(0,25), random.randint(0,25), 0, 800, 1, 0, 0]
		self.send_standard_packet(element)

		firgelli_down = [0, 0, 175, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_down)

		firgelli_up = [0, 0, 600, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)

	'Paint Routine for Creating the desired image'
	def Paint(self, LLT):

		# Record how far we've gone
		MAX_DIST = 2000
		paint_distance = MAX_DIST

		# Put Brush Down ? 
		put_brush_down = True

		# For every brush stroke represented in the LLT 
		for brush_stroke in LLT:
			
			# For every coordinate in the brush stroke
			for point_index in range(len(brush_stroke)) : 
				
				# If the paint distance has exceed the maximum alloted
				if(paint_distance >= MAX_DIST):

					# Get more paint and re-do the last few points
					self.getPaint()
					point_index = max(0,point_i-3)
					put_brush_down = True
					paint_distance = 0

				# Get next global position to move the gantry
				dx = brush_stroke[point_index][0]
				dy = brush_stroke[point_index][1]

				# Send element to arduino
				element = [dx, dy, 0, 800, 1, 0, 0]
				send_standard_packet(element)

				# The brush is currently down and paint is being applied, so increment paint distance
				if not put_brush_down:
					paint_distance += math.sqrt((dx-strokes[stroke_i][max(0,point_i-1)][0])**2 + (dy-strokes[stroke_i][max(0,point_i-1)][1])**2)
					print paint_distance

				# The brush needs to be put back down
				else:
					print "Putting Brush Down..."
					put_brush_down = False
					
					firgelli_down = [0, 0, 170, 800, 0, 1, 1]
					send_standard_packet(firgelli_down)


			# Done with current brush stroke
			firgelli_up = [0, 0, 600, 800, 0, 1, 1]
			send_standard_packet(firgelli_up)
			first_elem = True
			point_i=0
			stroke_i += 1
			if(MAX_DIST-paint_distance < 300):
				paint_distance = MAX_DIST

		# Paint Routine Complete pick up Fergelli and return to start
		firgelli_up = [0, 0, 600, 800, 0, 1, 1]
		send_standard_packet(firgelli_up)
		element = [0, 0, 0, 800, 1, 0, 0]
		send_standard_packet(element)








