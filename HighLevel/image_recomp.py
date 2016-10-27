#!/usr/bin/env python


import cv2
import numpy as np

#read image
img = cv2.imread('butterfly.jpg')

#find height and width of image
height,width,channels = img.shape
print height, width, channels

#create new image with same height and width
hatching = np.zeros((height, width, channels), np.uint8) #initializes image as black - HATCHING
crosshatching = np.zeros((height, width, channels), np.uint8) #initializes image as black - CROSSHATCHING
dot = np.zeros((height, width, channels), np.uint8) #initializes image as black - DOT


#Populate new image - HATCHING
pixelstepsize = 7
for x in range(1, height/pixelstepsize):
	for y in range(1, width/pixelstepsize):
		for step in range(0, pixelstepsize):
			hatching[(x*pixelstepsize)-step, (y*pixelstepsize)-step] = img[x*pixelstepsize, y*pixelstepsize]


#Populate new image - CROSSHATCHING
pixelstepsize = 7
for x in range(1, height/pixelstepsize):
	for y in range(1, width/pixelstepsize):
		for step in range(0, pixelstepsize):
			crosshatching[(x*pixelstepsize)-step, (y*pixelstepsize)-step] = img[x*pixelstepsize, y*pixelstepsize]
			crosshatching[(x*pixelstepsize)+step, (y*pixelstepsize)-step] = img[x*pixelstepsize, y*pixelstepsize]
			crosshatching[(x*pixelstepsize)-step, (y*pixelstepsize)+step] = img[x*pixelstepsize, y*pixelstepsize]
			crosshatching[(x*pixelstepsize)+step, (y*pixelstepsize)+step] = img[x*pixelstepsize, y*pixelstepsize]


#Populate new image - DOT
pixelstepsize = 10
for x in range(1, height/pixelstepsize):
	for y in range(1, width/pixelstepsize):
		for stepx in range(0, pixelstepsize):
			for stepy in range(0, pixelstepsize):
				dot[x*pixelstepsize+stepx-pixelstepsize/2, y*pixelstepsize+stepy-pixelstepsize/2] = img[x*pixelstepsize, y*pixelstepsize]


cv2.imwrite('hatching.jpg',hatching)#HATCHING
cv2.imwrite('crosshatching.jpg',crosshatching)#CROSSHATCHING
cv2.imwrite('dot.jpg', dot)#DOT

