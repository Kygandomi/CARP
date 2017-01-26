#! /usr/bin/env python
# MQP -- CARP Project
# Manual Gantry Control Class

import serial_communication as ser_comm
import math
from time import sleep

# Routine for sending a standard packet via Serial 
def send_standard_packet(packet):
	# Send a packet
	# arduino_ser.flush()
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
		while( parse_val != -1):
			read_val = arduino_ser.recieve_packet()
			parse_val = arduino_ser.parse_packet(read_val)
			sleep(0.1)
		print "Motion Complete!"



# Connect to Arduino over serial
baud = 115200

ports_list = ['COM3', '/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9']

for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if(arduino_ser.connect()):
		break

sleep(1)

##############################################################################
##############################################################################
##############################################################################

####### Square Calibration Routine ######
print "Square Calibration Routine"
# Standard PAcket: [x y z step_time xy_abs z_abs go_flag]
firgelli_up = [0, 0, 700, 800, 0, 1, 1]
firgelli_down = [0, 0, 340, 800, 0, 1, 1]

# Let's draw a square
send_standard_packet(firgelli_up)
# sleep(1)

# firgelli_up = [0, 0, 850, 800, 0, 1, 1]
# firgelli_down = [0, 0, 200, 800, 0, 1, 1]

# # move_to = [0, 190, 250, 800, 0, 1, 1]

# # send_standard_packet(move_to)
# # sleep(1)

# send_standard_packet([0, 0, 850, 800, 1, 1, 1])
# send_standard_packet([0, 400, 850, 800, 1, 1, 1])
# send_standard_packet([400, 400, 850, 800, 1, 1, 1])
# send_standard_packet([400, 0, 850, 800, 1, 1, 1])
# send_standard_packet([0, 0, 850, 800, 1, 1, 1])

##############################################################################

# PICK UP
# [x, y, z, step_time, xy_abs, z_abs, GO]

# offX=400
# offY=190
# up=850
# down=300

# send_standard_packet([0,0,up,800,1,1,1])
# sleep(1)
# send_standard_packet([0,offY,up,800,1,1,1])
# sleep(1)
# send_standard_packet([offX,offY,up,800,1,1,1])
# sleep(1)
# send_standard_packet([offX,offY,down,800,1,1,1])
# sleep(2)
# send_standard_packet([0,offY,down,800,1,1,1])

# PUT DOWN

# send_standard_packet([0,0,down,800,1,1,1])
# sleep(1)
# send_standard_packet([0,offY,down,800,1,1,1])
# sleep(1)
# send_standard_packet([offX,offY,down,800,1,1,1])
# sleep(1)
# send_standard_packet([offX,offY,up,800,1,1,1])
# sleep(2)
# send_standard_packet([0,offY,up,800,1,1,1])

##############################################################################

##############################################################################

# send_standard_packet(firgelli_down)
# send_special_packet()


# x=int(95.2119 *10.9)
# y=int(51.8287 *10.9)
# abs_flag = True

# move_to = [x,y,abs_flag,0,0,800]

# send_standard_packet(move_to)

# x=int(84.4169 * 10.9)
# y=int(54.2036 * 10.9)
# abs_flag = True

# move_to = [x,y,abs_flag,0,0,800]

# send_standard_packet(move_to)

# x=int(73.6219 * 10.9)
# y=int(57.8739 * 10.9)
# abs_flag = True

# move_to = [x,y,abs_flag,0,0,800]

# send_standard_packet(move_to)

# send_standard_packet(firgelli_up)
# send_special_packet()

##############################################################################

# # # Send A Single Packet to the Arduino
# m1_dir = 1 # +X 
# m1_steps = 0 # 4 Revolutions
# m1_step_time = 800 # In microseconds

# m2_dir = 0 # +Y
# m2_steps =  0 # 4 Revolution
# m2_step_time = 800 # In microseconds

# firgelli_pos = 400

# arduino_ser.send_packet(m1_dir, m1_steps, m1_step_time, m2_dir, m2_steps, m2_step_time, firgelli_pos)

##############################################################################

# Send Commands Arduino One After the Other
# index = 0
# directions_m1 = [0, 1, 1, 0, 0, 1]
# directions_m2 = [0, 0, 1, 1, 0, 1]
# firgelli_pos = [175, 175, 175, 175, 175, 700]

# steps = [600, 600, 600, 600, 600, 600]
# step_time = [800, 800, 800, 800, 800, 800]
# while(index < 6):
# 	read_val = arduino_ser.recieve_packet()
# 	if(arduino_ser.parse_packet(read_val) == -1):
# 		print "Sending Data"
# 		print index
# 		arduino_ser.send_packet(directions_m1[index], steps[index], step_time[index], directions_m2[index], steps[index], step_time[index], firgelli_pos[index])
# 		index+=1
# 		sleep(1);


# Disconnect Stream
arduino_ser.disconnect()



