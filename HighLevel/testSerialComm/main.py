#! /usr/bin/env python
# MQP -- CARP Project
# Main Class

import serial_communication as ser_comm
from time import sleep

sleep(1)

# Connect to Arduino over serial
baud = 115200
#port = '/dev/tty.usbserial-A902U9B9'
port = '/dev/tty.usbmodem1411'
arduino_ser = ser_comm.serial_comms(port, baud)
arduino_ser.connect()

sleep(1)

# Send a packet
m1_dir = 1 # +X 
m1_steps = 200 # 1 Revolution
m1_step_time = 200 # In microseconds

m2_dir = 1 # +Y
m2_steps =  200 # 0.5 Revolution
m2_step_time = 200 # In microseconds

# Send this to the Arduino por favor
arduino_ser.send_packet(m1_dir, m1_steps, m1_step_time, m2_dir, m2_steps, m2_step_time)


# arduino_ser.disconnect()