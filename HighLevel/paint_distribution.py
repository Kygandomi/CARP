#! /usr/bin/env python
# MQP -- CARP Project
from paint_with_pmd.painter_bot import *
from time import sleep
import cv2

##################################################################
##########################  SETUP  ###############################
##################################################################
print "Setup"

def gaussian_LLT(mu_x, sigma_x, mu_y, sigma_y, num_points):
	# Create Randomly distributed LLT
	print "Creating Distribution for LLT"
	out_pts = []
	list_pts=[]

	out_pts_scaled = []
	list_pts_scaled = []
	for i in range(0, num_points):
	    
	    x1 = abs(np.random.normal(mu_x, sigma_x, 1)[0])
	    y1 = abs(np.random.normal(mu_y, sigma_y, 1)[0])

	    list_pts.append([x1, y1,0])
	out_pts.append(list_pts)

	LLT = out_pts
	print LLT

	# testLLT(LLT,3)

	return LLT


##################################################################
######################## PAINT ROUTINE ###########################
##################################################################
# Lets Paint
bot = painter_bot()
bot.connect_camera([1,2,0])

# Variables for the distribution
canvas = bot.camera.get_canvas()
img_width = canvas.shape[0]
img_height = canvas.shape[1]

mu_x, sigma_x = img_width/2, 30
mu_y, sigma_y = img_height/2, 30

num_points = 100
number_of_colors = 3

bot.connect_eth(ip = '192.168.178.7',port = 1234)

bot.indeces=range(number_of_colors)

for i in range(number_of_colors):
	bot.lltListImg = [gaussian_LLT(mu_x, sigma_x, mu_y, sigma_y, num_points)]
	bot.paint()

print "Process Complete"

