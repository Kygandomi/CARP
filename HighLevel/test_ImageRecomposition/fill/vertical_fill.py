#! /usr/bin/env python

#Fills in an area of black with vertical lines
import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
import cv2
import numpy as np

brushSize = 5 #number of pixels in the radius of the brush

def display(img, name):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


img = cv2.imread('box.png', cv2.IMREAD_UNCHANGED) #image you want to create
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

#find start and end points based on the brush size
for y in range(0, height):
	if not stroke:
		for x in range(0, width):	
			if 0 in dilateImg[x,y] and line==False:
				startPoints.append([x,y])
				stroke = True
				newy = y + (2*brushSize)
				line = True
			if line==True and 0 not in dilateImg[x,y]:
				endPoints.append([x-1,y])
				line = False
	elif newy <= y:
		stroke = False


canvasImg = np.zeros((height, width, channels), np.uint8) #make new canvas the size of the original image
canvasImg.fill(255) #fill with white

for element in range(0, len(startPoints)-1):
	canvasImg[startPoints[element][0], startPoints[element][1]] = (0,0,0,255)
	canvasImg[endPoints[element][0], endPoints[element][1]] = (0,0,0,255)

display(canvasImg, "Finished Image") #displays start and end points only

#create txt document of the start/end of each stroke
pixelToMM = 10.9
orders = open("VertFillOrders.txt", 'w') #store points
for element in range(0, len(startPoints)-1):
	orders.write(str(startPoints[element][0]*pixelToMM)+' '+str(startPoints[element][1]*pixelToMM)+'\n')
	orders.write('\n')
orders.close()