#! /usr/bin/env python

#Fills in an area of black with horizontal lines
import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
import cv2
import numpy as np

brushSize = 10  #number of pixels in the radius of the brush

def display(img, name):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


img = cv2.imread('circle.png', cv2.IMREAD_UNCHANGED) #image you want to create
display(img, "Initial Image")

#dilate the image the radius of the brush
kernal = np.ones((brushSize,brushSize), np.uint8)
dilateImg = cv2.dilate(img,kernal,iterations = 1)
display(dilateImg, "Dilated Image")

#find height and width of image
height, width, channels = dilateImg.shape
startPoints = []
endPoints = []
line = False
stroke = False

#find all the start and end points based on the brush size
for x in range(0, height):
	if not stroke:
		for y in range(0, width):	
			if 0 in dilateImg[x,y] and line==False:
				startPoints.append([x,y])
				stroke = True
				newx = x + (2*brushSize)
				line = True
			if line==True and 0 not in dilateImg[x,y]:
				endPoints.append([x-1,y])
				line = False
	elif newx <= x:
		stroke = False


canvasImg = np.zeros((height, width, channels), np.uint8) #create canvas image same size as original
canvasImg.fill(255) #fill with white

for element in range(0, len(startPoints)-1):
	canvasImg[startPoints[element][0], startPoints[element][1]] = (0,0,0, 255)
	canvasImg[endPoints[element][0], endPoints[element][1]] = (0,0,0, 255)

display(canvasImg, "Finished Image") #displays the start and end positions only

#create txt document of the start/end of each stroke
pixelToMM = (8.5*25.4)/width
orders = open("HorFillOrders.txt", 'w') #store points
for element in range(0, len(startPoints)-1):
	orders.write(str(startPoints[element][0]*pixelToMM)+' '+str(startPoints[element][1]*pixelToMM)+'\n')
	orders.write(str(endPoints[element][0]*pixelToMM)+' '+str(endPoints[element][1]*pixelToMM) +'\n')
	orders.write('\n')
orders.close()