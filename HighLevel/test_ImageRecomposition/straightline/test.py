import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import numpy as np
import cv2
import random
import math

def display(img, name):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def makeStroke(canvas, stroke, pos):
	"""Places nontransperant pixels from the stroke image into the canvas image.
	pos is the position on the CANVAS where the (0,0) pixel from the STROKE will be placed."""
	offsetx , offsety = pos
	canvas_cols, canvas_rows, canvas_channels = canvas.shape
	stroke_cols, stroke_rows, stroke_channels = stroke.shape
	for x in range(0, stroke_cols):
		for y in range (0, stroke_rows):
			if ((stroke[x, y])[3] > 3):
				#print "painting position: ", offsetx + x, " ", offsety + y
				try:
					canvas[offsetx + x, offsety + y] = stroke[x, y]
				except IndexError:
					pass
	return canvas

def makeStrokeResize(canvas, stroke, pos):
	"""Currently broken, but I also think we might just not need it."""
	resize_dim = 100

	canvas_cols, canvas_rows, canvas_channels = canvas.shape
	stroke_cols, stroke_rows, stroke_channels = stroke.shape

	stroke_resize_dim_x = resize_dim / (canvas_rows/stroke_rows)
	stroke_resize_dim_y = resize_dim / (canvas_cols/stroke_cols)


	canvas_resize = cv2.resize(canvas, (resize_dim,resize_dim))
	stroke_resize = cv2.resize(stroke, (stroke_resize_dim_x,stroke_resize_dim_y))

	offsetx, offsety = pos

	offsetx = int(offsetx * float(resize_dim)/float(canvas_rows))
	offsety = int(offsety * float(resize_dim)/float(canvas_cols))

	new = makeStroke(canvas_resize, stroke_resize, (offsetx, offsety))
	new = cv2.resize(new, (canvas_rows, canvas_cols))
	return new

def calcMSE(img1, img2):
	sum = 0.0
	resized_img1 = cv2.resize(img1, (100, 100)) 
	resized_img2 = cv2.resize(img2, (100, 100)) 
	return cv2.norm(resized_img1, resized_img2, cv2.NORM_L1)

def convertPix_mm_string(pix, canvas_dimensions):
	"""Returns a pair of float value, pixels coordinates to milimetres coordiantes.
	This conversion is based on the number of pixels and the size of the image canvas,
	and uses values based on an 8.5x11in page.
	Pix should be a tuple, canvas dimension an int or float."""
	x, y = pix
	canvas_cols, canvas_rows = canvas_dimensions
	return str(((y)*1.0)*(8.5*25.4/canvas_cols)) + " " + str(((x)*1.0)*(11*25.4/canvas_rows))

stroke1Img = cv2.imread('stroke1.png', cv2.IMREAD_UNCHANGED)
stroke2Img = cv2.imread('stroke2.png', cv2.IMREAD_UNCHANGED)
# stroke3Img = cv2.imread('stroke3.png', cv2.IMREAD_UNCHANGED)
# stroke4Img = cv2.imread('stroke4.png', cv2.IMREAD_UNCHANGED)
desiredImg = cv2.imread('box.png', cv2.IMREAD_UNCHANGED)
canvasImg = cv2.imread('canvas.png', cv2.IMREAD_UNCHANGED)

display(desiredImg, 'desiredImg')
#display(canvasImg, 'canvasImg')
#display(strokeImg, 'strokeImg')

canvas_cols, canvas_rows, canvas_channels = canvasImg.shape
#stroke_rows, stroke_cols, stroke_channels = strokeImg.shape

strokeLibrary = [stroke1Img, stroke2Img]#, stroke3Img, stroke4Img]

strokes = 0
strokesToMake = 50

childrenPerGeneration = 50

orders = open("orders.txt", 'w')

currentBestCanvas = canvasImg.copy()

while(strokes < strokesToMake):
	possible_canvases = []
	bestError = 9999999999 # @TODO: Make this not stupid
	numBestError = 0
	painted_canvases = []
	strokeCoordinates = [] 
	strokeType = 0 # This keeps track of the selected stroke. 

	for i in range(0, childrenPerGeneration):
		canvas = currentBestCanvas.copy()
		possible_canvases.append(canvas)

	i = 0
	for canvas_to_paint_randomly in possible_canvases:
		strokeType = random.randint(0, len(strokeLibrary)-1)
		chosenStroke = strokeLibrary[strokeType]

		stroke_cols, stroke_rows, stroke_channels = chosenStroke.shape

		limit_y = canvas_cols - stroke_cols
		limit_x = canvas_rows - stroke_rows
		x = random.randint(0,limit_x)
		y = random.randint(0,limit_y)
		canvas_to_paint_randomly = makeStroke(canvas_to_paint_randomly, chosenStroke, (x, y))
		painted_canvases.append(canvas_to_paint_randomly)

		#display(canvas_to_paint_randomly, "RR")
		#cv2.imwrite("zimg" + str(strokes) + "_" + str(i) + ".png", canvas_to_paint_randomly)

		strokeStartCoord = convertPix_mm_string((y,x), (canvas_cols, canvas_rows))
		strokeEndCoord = (0,0) # Initialize, but do not ever use this val.

		if strokeType == 0: # Horisontal strokes
			strokeEndCoord = convertPix_mm_string((y+stroke_cols, x), (canvas_cols, canvas_rows))
		elif strokeType == 1: # Vertial strokes
			strokeEndCoord = convertPix_mm_string((y, x+stroke_rows), (canvas_cols, canvas_rows))
		strokeCoordinates.append(str(strokeStartCoord + strokeEndCoord))
		i+=1

	for i in range(0, childrenPerGeneration):
		mse = calcMSE(painted_canvases[i], desiredImg)
		if mse < bestError:
			bestError = mse
			numBestError = i

	print "Best one was number ", numBestError
	currentBestCanvas = painted_canvases[numBestError]
	orders.write(strokeCoordinates[numBestError] + '\n')
	strokes += 1
	print "Strokes remaining: ", strokesToMake- strokes

display(currentBestCanvas, "Hey did it work?")

print "Done"