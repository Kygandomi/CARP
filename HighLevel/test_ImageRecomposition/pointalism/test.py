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
			if ((strokeImg[x, y])[3] > 3):
				canvas[offsetx + x, offsety + y] = stroke[x, y]
	return canvas

def calcMSE(img1, img2):
	sum = 0.0
	resized_img1 = cv2.resize(img1, (100, 100)) 
	resized_img2 = cv2.resize(img2, (100, 100)) 
	return cv2.norm(resized_img1, resized_img2, cv2.NORM_L1)

strokeImg = cv2.imread('stroke.png', cv2.IMREAD_UNCHANGED)
desiredImg = cv2.imread('circle.png', cv2.IMREAD_UNCHANGED)
canvasImg = cv2.imread('canvas.png', cv2.IMREAD_UNCHANGED)

display(desiredImg, 'desiredImg')
display(canvasImg, 'canvasImg')
display(strokeImg, 'strokeImg')

canvas_rows, canvas_cols, canvas_channels = canvasImg.shape
stroke_rows, stroke_cols, stroke_channels = strokeImg.shape

strokes = 0
strokesToMake = 60

childrenPerGeneration = 18

currentBestCanvas = canvasImg.copy()

orders = open("orders.txt", 'w')

while(strokes < strokesToMake):
	possible_canvases = []
	strokeCoordinates = [] 

	bestError = 9999999999 # @TODO: Make this not stupid
	numBestError = 0

	for i in range(0, childrenPerGeneration):
		canvas = currentBestCanvas.copy()
		possible_canvases.append(canvas)

	i = 0
	for canvas_to_paint_randomly in possible_canvases:
		limit_x = canvas_cols - stroke_cols
		limit_y = canvas_rows - stroke_rows
		x = random.randint(0,limit_x)
		y = random.randint(0,limit_y)
		canvas_to_paint_randomly = makeStroke(canvas_to_paint_randomly, strokeImg, (x, y))
		strokeCoordinates.append(str((x*1.0)*(8.5*25.4/1000)) + " " + str((y*1.0)*(11*25.4/1000)))
		# print "MSE for current canvas:", mse
		# display(canvas_to_paint_randomly, "New canvas")
		# cv2.imwrite("zimg" + str(strokes) + "_" + str(i) + ".png", canvas_to_paint_randomly)
		i+=1
		


	for i in range(0, childrenPerGeneration):
		mse = calcMSE(possible_canvases[i], desiredImg)
		if mse < bestError:
			bestError = mse
			numBestError = i
	print "Best one was number ", numBestError
	currentBestCanvas = possible_canvases[numBestError]
	orders.write(strokeCoordinates[numBestError] + '\n')
	

	strokes += 1
display(currentBestCanvas, "Hey did it work?")
display(currentBestCanvas, "Hey did it work?")

print "Done"