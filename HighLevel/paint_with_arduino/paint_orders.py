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
			sleep(0.1)

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
			sleep(1)

	'Routine for getting brush'
	def getBrush(self, old_brush_index, new_brush_index):
		print "Switching Brushes ..."

		firgelli_insert_height = 300
		firgelli_lift_out_height = 850
		x_depth = 400

		firgelli_up = [0, 0, firgelli_insert_height, 800, 0, 1, 1]

		brush_offsets = [[3300,1900],[3300,1250]]

		# put current brush back
		placeBrush(brush_offsets[old_brush_index])

		# get new brush pos
		pickBrush(brush_offsets[new_brush_index])

		def pickBrush(offset_point):
			offX=offset_point[0]
			offY=offset_point[1]

			send_standard_packet([offX,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX+x_depth,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX+x_depth,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)

		def placeBrush(offset_point):
			offX=offset_point[0]
			offY=offset_point[1]

			send_standard_packet([offX,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX+x_depth,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX+x_depth,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			send_standard_packet([offX,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)


	'Routine for reloading paint on the brush'
	def getPaint(self, well_index):
		print "Getting Paint ..."

		# Fergelli Height Values
		down_val = 373
		up_val = 800

		# Get Paint Routine
		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)

		element = [random.randint(0,100), random.randint(0,100), 0, 800, 1, 0, 0]
		self.send_standard_packet(element)

		firgelli_down = [0, 0, down_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_down)

		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)

	'Paint Routine for Creating the desired image'
	def Paint(self, LLT):
		# Scale 
		scale_val = 8.7

		# Record Fergelli Height Values
		down_val = 350
		up_val = 550
		final_up_val = 800

		# Record how far we've gone (0.1 mm)
		MAX_DIST = 1342
		MAX_DIST_END = 500
		DOWN_COST = 50
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
					point_index = max(0,point_index-3)
					put_brush_down = True
					paint_distance = 0

				# Get next global position to move the gantry
				dx = int(brush_stroke[point_index][0] * scale_val)
				dy = int(brush_stroke[point_index][1] * scale_val)

				# Send element to arduino
				element = [dx, dy, 0, 800, 1, 0, 0]
				self.send_standard_packet(element)

				# The brush is currently down and paint is being applied, so increment paint distance
				if not put_brush_down:
					paint_distance += math.sqrt((dx-(brush_stroke[max(0,point_index-1)][0]*scale_val))**2 + (dy-(brush_stroke[max(0,point_index-1)][1]*scale_val))**2)
					print "distance: ", paint_distance

				# The brush needs to be put back down
				if put_brush_down: 
					print "Putting Brush Down..."
					put_brush_down = False
					paint_distance += DOWN_COST
					firgelli_down = [0, 0, down_val, 800, 0, 1, 1]
					self.send_standard_packet(firgelli_down)


			# Done with current brush stroke
			firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
			self.send_standard_packet(firgelli_up)
			put_brush_down  = True
			if(MAX_DIST-paint_distance < MAX_DIST_END):
				paint_distance = MAX_DIST

		# Paint Routine Complete pick up Fergelli and return to start
		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)
		element = [0, 0, final_up_val, 800, 1, 1, 1]
		self.send_standard_packet(element)








