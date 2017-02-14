#! /usr/bin/env python
# MQP -- CARP Project
# Manual Gantry Control Class via Ethernet

import ethernet_communication as eth_comm
import math
from time import sleep

# Connect to PMD over ethernet
ip = '192.168.178.7'
port = 1234
pmd_com = eth_comm.ethernet_comms(ip, port)

connected = False

#while not connected:
connected = pmd_com.connect()
if not connected: 
    exit()

packet = [0, 0, 500, 800, 1, 1, 1]
send_num = 1

while(send_num > 0):
	pmd_com.send_standard_packet(packet)
	send_num -= 1
	print "sending"

print "all sent"

sleep(1.5)

parse_val = 1

# Interpret incoming signals
read_val = pmd_com.recieve_packet()
print "read val ", read_val
sleep(0.1)
parse_val = pmd_com.parse_packet(read_val)
print "parse val ", parse_val
sleep(5)