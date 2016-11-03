#! /usr/bin/env python
# MQP -- CARP Project
# Main Class

import serial_communication as ser_comm
import math
from time import sleep

sleep(1)

# Connect to Arduino over serial
baud = 115200
#port = '/dev/tty.usbserial-A902U9B9'
port = '/dev/tty.usbmodem1411'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

sleep(1)

# # Send A Single Packet to the Arduino
# m1_dir = 1 # +X 
# m1_steps = 0 # 4 Revolutions
# m1_step_time = 800 # In microseconds

# m2_dir = 0 # +Y
# m2_steps =  0 # 4 Revolution
# m2_step_time = 800 # In microseconds

# fergelli_pos = 700

# arduino_ser.send_packet(m1_dir, m1_steps, m1_step_time, m2_dir, m2_steps, m2_step_time, fergelli_pos)

# Send Commands Arduino One After the Other
# index = 0
# directions_m1 = [0, 1, 1, 0, 0, 1]
# directions_m2 = [0, 0, 1, 1, 0, 1]
# fergelli_pos = [175, 175, 175, 175, 175, 700]

# steps = [600, 600, 600, 600, 600, 600]
# step_time = [800, 800, 800, 800, 800, 800]
# while(index < 6):
# 	read_val = arduino_ser.recieve_packet()
# 	if(arduino_ser.parse_packet(read_val) == -1):
# 		print "Sending Data"
# 		print index
# 		arduino_ser.send_packet(directions_m1[index], steps[index], step_time[index], directions_m2[index], steps[index], step_time[index], fergelli_pos[index])
# 		index+=1
# 		sleep(1);


# Disconnect Stream
arduino_ser.disconnect()



