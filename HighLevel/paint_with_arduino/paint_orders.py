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
	def __init__(self, com_obj):
		# Save the ser com to use
		self.com_obj = com_obj
		self.old_brush_index = -1
		self.well_index = -1

		# Arduino
		# self.brush_offsets = [[3420, 90],[3420,590],[3420,1090]]
		# self.well_offsets = [[3420, 90],[3420,590],[3420,1090]]

		# # PMD
		self.brush_offsets = [[3440, 90],[3440,590],[3440,1090]]
		self.well_offsets = [[3440, 90],[3440,590],[3440,1090]]

	'Routine for sending a standard packet via Serial' 
	def send_standard_packet(self, packet, wait=False):
		# For our convenience a Standard Packet Consists of : 
		# [x,y,z, min_step_time, xy_abs_flag, z_abs_flag, go_flag] 

		# Send a standard packet to the arduino
		self.com_obj.flush()
		self.com_obj.send_standard_packet(packet)

		# Check the go flag -- not go time
		if(packet[6] == 0):
			# Wait a bit for Arduino to process point
			sleep(0.1)

		# Check the go flag -- its go time
		elif(packet[6] == 1 and wait):
			# Interpret incoming signals
			read_val = self.com_obj.recieve_packet()
			print "buff size: ", len(read_val)
			parse_val = self.com_obj.parse_packet(read_val)

			# While the gantry has not completed its motion routine
			while( parse_val != 0):
				# Interpret incoming signals
				read_val = self.com_obj.recieve_packet()
				parse_val = self.com_obj.parse_packet(read_val)
				# if read_val != []:
				# 	print "Readval: ", read_val
				# if parse_val != -1:
				# 	print "parseval: ", parse_val
				sleep(0.1)
			print "Brush Stroke Motion Complete."

			# Sleep for a bit for the firgelli
			sleep(1)

	'Move the gantry to a particular location'
	def moveGantry(self, x, y):
		element = [x, y, 0, 800, 1, 0, 0]
		self.send_standard_packet(element)

	'Routine for getting brush'
	def getBrush(self, new_brush_index):
		print "Switching Brushes ..."

		firgelli_extract_height = 550 # 550
		firgelli_insert_height = 550 # 630 
		firgelli_lift_out_height = 900 # 950 
		x_depth = 400

		def pickBrush(offset_point):
			offX=offset_point[0]
			offY=offset_point[1]

			self.send_standard_packet([offX,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX+x_depth,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX+x_depth,offY,firgelli_extract_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX,offY,firgelli_extract_height,800,1,1,1])
			sleep(1)

		def placeBrush(offset_point):
			offX=offset_point[0]
			offY=offset_point[1]

			self.send_standard_packet([offX,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX+x_depth,offY,firgelli_insert_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX+x_depth,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)
			self.send_standard_packet([offX,offY,firgelli_lift_out_height,800,1,1,1])
			sleep(1)

		# put current brush back
		if(self.old_brush_index != -1):
			placeBrush(self.brush_offsets[self.old_brush_index])
		
		# If we dont want a new brush, return
		if(new_brush_index == -1 ):
			self.old_brush_index = new_brush_index
			return

		new_brush_index = new_brush_index%len(self.brush_offsets)

		# get new brush 
		pickBrush(self.brush_offsets[new_brush_index])

		print "Old index ", self.old_brush_index
		print "New index ", new_brush_index 

		# Save old brush
		self.old_brush_index = new_brush_index
		self.well_index = new_brush_index

	'Routine for reloading paint on the brush'
	def getPaint(self):
		print "Getting Paint ..."

		# Fergelli Height Values
		down_val = 270
		up_val = 800

		offX=self.well_offsets[self.well_index][0]
		offY=self.well_offsets[self.well_index][1]

		if(self.well_index < 0):
			offX = 0
			offY = 0

		# Get Paint Routine
		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)
		
		element = [min(random.randint(offX,offX+80), 4220), min(random.randint(offY,offY+5), 2440), 0, 800, 1, 0, 0]
		self.send_standard_packet(element)

		firgelli_down = [0, 0, down_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_down)

		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)

	def returnToStart(self):
		print "Returning brush"
		self.getBrush(-1)
		sleep(1)
		up_val = 800
		final_up_val = 800
		# Paint Routine Complete pick up Fergelli and return to start
		print "Returning to home"
		firgelli_up = [0, 0, up_val, 800, 0, 1, 1]
		self.send_standard_packet(firgelli_up)
		element = [100, 100, final_up_val, 800, 1, 1, 1]
		self.send_standard_packet(element,True)

	'Paint Routine for Creating the desired image'
	def Paint(self, LLT):
		# Scale 
		scale_val = 1

		# Record Fergelli Height Values
		down_val = 270
		up_val = 400
		final_up_val = 800

		# Record how far we've gone (0.1 mm)
		MAX_DIST = 2000
		MAX_DIST_END = 600
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
