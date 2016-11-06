import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import numpy as np
import cv2
import random

def display(img, name):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def makeStroke(canvas, stroke, pos):
	"""Places nontransperant pixels from the stroke image into the canvas image.
	pos is the position on the CANVAS where the (0,0) pixel from the STROKE will be placed."""
	offsetx, offsety = pos # Depackage the x and y positions
	canvas_rows, canvas_cols, canvas_channels = canvas.shape # Get the canvas image info
	stroke_rows, stroke_cols, stroke_channels = stroke.shape # Get the strome image info
	for x in range(0, stroke_cols): # For each column in the stroke
		for y in range (0, stroke_rows): # For each row in the stroke
			if ((stroke[x, y])[3] > 120): # If it is a nontransperant pixel
				canvas[offsetx + x, offsety + y] = stroke[x, y] # Attempt to paint that pixel to the canvas
	return canvas

orders = open("catordersSmallBrush2.txt", 'r')
#orders = open("x1_y1_test.txt", 'r')
canvasImg = cv2.imread('canvas.png', cv2.IMREAD_UNCHANGED)
strokeImg = cv2.imread('smallstroke.png', cv2.IMREAD_UNCHANGED)

katie_conversion = 1 # 10.9

#canvasImg = makeStroke(canvasImg, strokeImg, (0,0))
canvasImg = makeStroke(canvasImg, strokeImg, (0,250))
#canvasImg = makeStroke(canvasImg, strokeImg, (250,0))
#canvasImg = makeStroke(canvasImg, strokeImg, (250,250))

for line in orders:
	lineData = line.split(" ")
	x = int(float(lineData[0])/katie_conversion)
	y = lineData[1]
	y = int(float(y[:-2])/katie_conversion)
	print x, " ", y
	canvasImg = makeStroke(canvasImg, strokeImg, (x,y) )
display(canvasImg, "TEST")