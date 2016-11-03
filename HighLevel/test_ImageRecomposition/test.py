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
	offsetx , offsety = pos
	canvas_rows, canvas_cols, canvas_channels = canvas.shape
	stroke_rows, stroke_cols, stroke_channels = strokeImg.shape
	for x in range(0, stroke_rows):
		for y in range (0, stroke_cols):
			canvas[offsetx + x, offsety + y] = stroke[x, y]
	return canvas

def calcMSE(img1, img2):
	sum = 0.0
	resized_img1 = cv2.resize(img1, (256, 256)) 
	resized_img2 = cv2.resize(img2, (256, 256)) 

	return cv2.norm(resized_img1, resized_img2, cv2.NORM_L1)

	# r,c,l = resized_img1.shape
	# R,C,L = resized_img2.shape 
	# if r == R and c == C:
	# 	for x in range(0, r):
	# 	   for y in range(0, c):
	# 	      difference = (resized_img1[x,y] - resized_img2[x,y])
	# 	      sum = sum + difference*difference
	# mse = sum /(r*c)
	# print mse
	# return mse[0]


strokeImg = cv2.imread('stroke.png')
desiredImg = cv2.imread('box.png')
canvasImg = cv2.imread('canvas.png')

display(desiredImg, 'desiredImg')
display(canvasImg, 'canvasImg')
display(strokeImg, 'strokeImg')

canvas_rows, canvas_cols, canvas_channels = canvasImg.shape
stroke_rows, stroke_cols, stroke_channels = strokeImg.shape


strokes = 0
strokesToMake = 100

childrenPerGeneration = 10

currentBestCanvas = canvasImg.copy()

while(strokes < strokesToMake):
	possible_canvases = []
	bestError = 9999999999
	numBestError = 0

	for i in range(0, childrenPerGeneration):
		canvas = currentBestCanvas.copy()
		possible_canvases.append(canvas)

	for canvas_to_paint_randomly in possible_canvases:
		limit_x = canvas_cols - stroke_cols
		limit_y = canvas_rows - stroke_rows
		x = random.randint(0,limit_x)
		y = random.randint(0,limit_y)
		canvas_to_paint_randomly = makeStroke(canvas_to_paint_randomly, strokeImg, (x, y))
		mse = calcMSE(canvas_to_paint_randomly, desiredImg)
		# print "MSE for current canvas:", mse
		# display(canvas_to_paint_randomly, "New canvas")
		


	for i in range(0, childrenPerGeneration):
		mse = calcMSE(possible_canvases[i], desiredImg)
		if mse < bestError:
			bestError = mse
			numBestError = i
	print "Best one was number ", numBestError
	currentBestCanvas = possible_canvases[numBestError]
	

	strokes += 1
display(currentBestCanvas, "Hey did it work?")
display(currentBestCanvas, "Hey did it work?")
display(currentBestCanvas, "Hey did it work?")

# print "The mean square errors are:",mse2, mse3, mse4, mse5
print "Done"