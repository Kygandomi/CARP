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
pmd_com.connect()

packet = [1, 2, 3, 4, 5, 6, 7]
send_num = 1

while(send_num > 0):
	pmd_com.send_standard_packet(packet)
	send_num -= 1
	print "sending"

while( parse_val != 0):
	# Interpret incoming signals
	read_val = pmd_com.recieve_packet()
	print "read val ", read_val
	parse_val = pmd_com.parse_packet(read_val)
	print "parse_val", parse_val
	sleep(0.1)