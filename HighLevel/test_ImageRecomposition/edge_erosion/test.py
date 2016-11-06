import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import numpy as np
import cv2
import random

def display(img, name):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def save(img, name):
	cv2.imwrite(name+".png", img)

def output(img,name):
	save(img,name)
	display(img,name)

def autoCanny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
 
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
 
	# return the edged image
	return edged

def edgeIm_to_binImg(edgeImg):
	# TODO: convert edges to contoured regions (eliminate duplicate contours)
	pass

#######################################################################################
###################     Required Helper Functions      ################################
#######################################################################################

def parents(hierarchy):
	# [Next, Prev, 1st Child, Parent]
	i=0
	h_out = []
	for count in range(len(hierarchy)):
		if(hierarchy[i][0] == -1):
			h_out.append(i)
			return h_out
		else:
			h_out.append(i)
			i=hierarchy[i][0]
	return h_out

def childrenOf(hierarchy, i):
	# [Next, Prev, 1st Child, Parent]
	h_out = []
	for count in range(len(hierarchy)):
		if(hierarchy[count][3] == i):
			h_out.append(count)
	return h_out

def ptsInContours(contours,shape):
	cntr_pts = []
	# For each list of contour points...
	for i in range(len(contours)):
	    # Create a mask image that contains the contour filled in
	    cimg = np.zeros(shape)
	    cv2.drawContours(cimg, contours, i, color=255, thickness=-1)

	    # Access the image pixels and create a 1D numpy array then add to list
	    pts = np.where(cimg == 255)
	    real_pts = []
	    for j in range(len(pts[0])):
	    	real_pts.append((pts[1][j],pts[0][j]))
	    cntr_pts.append(real_pts)
	return cntr_pts

def rawPolyDist(bin_img):
	contourImg, contours, hierarchy = cv2.findContours(binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
	hierarchy = hierarchy[0]

	rawPolyImg = -1*np.ones(bin_img.shape)

	cntr_pts = ptsInContours(contours,binImg.shape)
	i_parents = parents(hierarchy)
	count = 1
	max_count = len(i_parents)
	for cnt_i in i_parents:
		print "Analyzing Contour "+str(count)+" of "+str(max_count)
		list_pts = cntr_pts[cnt_i]
		for pt in list_pts:
			value = cv2.pointPolygonTest(contours[cnt_i],pt,True)
			if(hierarchy[cnt_i][2]!=-1):
				min_val2 = 1
				for child_i in childrenOf(hierarchy,cnt_i):
					value2 = cv2.pointPolygonTest(contours[child_i],pt,True)
					min_val2 = min(min_val2,value2)
				value = min(value,-min_val2)
			rawPolyImg.itemset((pt[1],pt[0]),value)
		count = count + 1
	print "Contour Analysis Complete"
	return rawPolyImg

#######################################################################################
###################     Required Helper Functions      ################################
#######################################################################################
	
desiredImg = cv2.imread('fish.png', cv2.IMREAD_UNCHANGED)
canvasImg = cv2.imread('canvas.png', cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)

desired_rows, desired_cols = desiredImg_grey.shape
canvas_rows, canvas_cols, canvas_channels = canvasImg.shape

(thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#binImg = autoCanny(desiredImg)

binImg = 255-binImg

rawPolyImg = rawPolyDist(binImg)

mini,maxi = np.abs(cv2.minMaxLoc(rawPolyImg)[:2])          # Find minimum and maximum to adjust colors
mini = 255.0/mini
maxi = 255.0/maxi

polyDist = desiredImg.copy()

for i in xrange(desired_rows):                              
    for j in xrange(desired_cols):
        if rawPolyImg.item((i,j))<0:
            polyDist.itemset((i,j,0),255-int(abs(rawPolyImg.item(i,j))*mini))   # If outside, blue color
            polyDist.itemset((i,j,1),0)
            polyDist.itemset((i,j,2),0)
        elif rawPolyImg.item((i,j))>0:
        	polyDist.itemset((i,j,0),0)
    		polyDist.itemset((i,j,1),0)
    		polyDist.itemset((i,j,2),255-int(rawPolyImg.item(i,j)*maxi))        # If inside, red color
        else:
            polyDist.itemset((i,j,0),255)
            polyDist.itemset((i,j,1),255)
            polyDist.itemset((i,j,2),255)                            # If on the contour, white color.


output(polyDist, 'outImg')

print "Done"
