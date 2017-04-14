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

packet_list=[]

# 3840, 90, 550
# packet_list.append([0,0, 800, 800, 1, 1, 1])

# offset = 0
# size = 2400
# n_iter = 0
# for i in range(n_iter):
#     packet_list.append([size+offset*i, offset*i, 600, 800, 1, 1, 0])
#     packet_list.append([size+offset*i, size+offset*i, 600, 800, 1, 1, 0])
#     packet_list.append([offset*i, size+offset*i, 600, 800, 1, 1, 0])
#     packet_list.append([offset*i, offset*i, 600, 800, 1, 1, 0])

packet_list.append([383, 252, 850, 800, 1, 1, 1])

for packet in packet_list:
    print "sending"
    pmd_com.send_standard_packet(packet)

print "all sent"

sleep(1)

# parse_val = 1

# # Interpret incoming signals
# while not (parse_val==0 or parse_val==1):
#     read_val = pmd_com.recieve_packet()
#     # print "read val ", read_val
#     sleep(0.1)
#     parse_val = pmd_com.parse_packet(read_val)
#     print "parse val: ", parse_val
