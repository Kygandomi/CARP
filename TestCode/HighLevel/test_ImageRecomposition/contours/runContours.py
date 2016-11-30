import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import numpy as np
import cv2
import random

def display(img, name=""):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def save(img, name="outImg"):
	cv2.imwrite(name+".png", img)

def output(img,name="outImg"):
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

def findRidges(polyImg):
	# TODO: find ridges, "lines" which are as far from edges as possible
	pass

#######################################################################################
###################     Required Helper Functions      ################################
#######################################################################################

def circleKernal(radius, value=1):
	brush = cv2.circle(np.zeros((radius*2+1,radius*2+1)),(radius,radius),radius,value,-1).astype('uint8')

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

def getPoints(img,color=255):
	pts = np.where(img == 255)
	real_pts = []
	for j in range(len(pts[0])):
		real_pts.append((pts[0][j],pts[1][j]))
	return real_pts

def intersect(img1,img2,color=255):
	path =  cv2.bitwise_and((color-img1),cv2.erode(img2,circleKernal(1),iterations=1))
	mini,maxi = cv2.minMaxLoc(path)[:2]
	nonzero = path[path > 0]
	mid = np.median(nonzero)
	sigma = .5
	(thresh, pathImg) = cv2.threshold(path,sigma*maxi+(1-sigma)*mid, 255, cv2.THRESH_BINARY)
	return pathImg

def ptsInContours(contours,hierarchy,shape,):
	cntr_pts = []
	# For each list of contour points...
	for i in range(len(contours)):
		# Create a mask image that contains the contour filled in
		cimg = np.zeros(shape)
		cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
		
		if(hierarchy[i][2]!=-1):
			cimg = cv2.erode(cimg, circleKernal(5))
			for child_i in childrenOf(hierarchy,i):
				cv2.drawContours(cimg, contours, child_i, color=0, thickness=-1)
			cimg = cv2.dilate(cimg, circleKernal(5))
		# Access the image pixels and create a 1D numpy array then add to list
		cntr_pts.append(getPoints(cimg))
	return cntr_pts

def rawPolyDist(bin_img):
	contourImg, contours, hierarchy = cv2.findContours(binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
	hierarchy = hierarchy[0]

	rawPolyImg = np.array(-1.0*np.ones(bin_img.shape),dtype='float32')

	cntr_pts = ptsInContours(contours,hierarchy,binImg.shape)
	i_parents = parents(hierarchy)
	count = 1
	max_count = len(i_parents)
	for cnt_i in i_parents:
		print "Analyzing Contour "+str(count)+" of "+str(max_count)
		list_pts = cntr_pts[cnt_i]
		for pt in list_pts:
			value = cv2.pointPolygonTest(contours[cnt_i],(pt[1],pt[0]),True)
			if(hierarchy[cnt_i][2]!=-1):
				min_val2 = 1
				for child_i in childrenOf(hierarchy,cnt_i):
					value2 = cv2.pointPolygonTest(contours[child_i],(pt[1],pt[0]),True)
					min_val2 = min(min_val2,value2)
				value = min(value,-(min_val2))
			rawPolyImg.itemset(pt,value)
		count = count + 1
	print "Contour Analysis Complete"
	return rawPolyImg, contours, hierarchy, cntr_pts

def scaledPolyDist(rawPolyImg):
	mini,maxi = np.abs(cv2.minMaxLoc(rawPolyImg)[:2])          # Find minimum and maximum to adjust colors
	#print "Min: "+str(mini)+" | Max: "+str(maxi)
	maxi = 255.0/maxi

	scaledPolyImg = np.array(-1*np.ones(rawPolyImg.shape),dtype='uint8')

	for i in xrange(rawPolyImg.shape[0]):                              
	    for j in xrange(rawPolyImg.shape[1]):
	        if rawPolyImg.item((i,j))>0:
	        	scaledPolyImg.itemset((i,j),255-int(rawPolyImg.item(i,j)*maxi))        # If inside, gradient to dark
	        else:
	        	scaledPolyImg.itemset((i,j),255)        # If outside, white

	return scaledPolyImg

def visualPolyDist(rawPolyImg):
	mini,maxi = np.abs(cv2.minMaxLoc(rawPolyImg)[:2])          # Find minimum and maximum to adjust colors
	#print "Min: "+str(mini)+" | Max: "+str(maxi)
	mini = 255.0/mini
	maxi = 255.0/maxi

	visualPolyImg = cv2.cvtColor(np.array(-1*np.ones(rawPolyImg.shape),dtype='uint8'),cv2.COLOR_GRAY2RGB)

	for i in xrange(desired_rows):                              
	    for j in xrange(desired_cols):
	        if rawPolyImg.item((i,j))<0:
	            visualPolyImg.itemset((i,j,0),255-int(abs(rawPolyImg.item(i,j))*mini))   # If outside, blue color
	            visualPolyImg.itemset((i,j,1),0)
	            visualPolyImg.itemset((i,j,2),0)
	        elif rawPolyImg.item((i,j))>0:
	        	visualPolyImg.itemset((i,j,0),0)
	    		visualPolyImg.itemset((i,j,1),0)#+int(rawPolyImg.item(i,j)*maxi))
	    		visualPolyImg.itemset((i,j,2),255-int(rawPolyImg.item(i,j)*maxi))        # If inside, red color
	        else:
	            visualPolyImg.itemset((i,j,0),255)
	            visualPolyImg.itemset((i,j,1),255)
	            visualPolyImg.itemset((i,j,2),255)                            # If on the contour, white color.
	return visualPolyImg

#######################################################################################
###################     Required Helper Functions      ################################
#######################################################################################
	
desiredImg = cv2.imread('../images/twocarp.png', cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)
(thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#binImg = autoCanny(desiredImg)
# display(binImg)
binImg = 255-binImg

rawPolyImg,contours,hierarchy,cntr_pts = rawPolyDist(binImg)

############################################################################
############################################################################
############################################################################

polyImg = scaledPolyDist(rawPolyImg)

display(polyImg)

##Adaptive Threshold: Gaussian
## Somewhat decent, parameters must be tuned to specific image
## Not ideal because doesnt take derivitive
#pathImg = cv2.adaptiveThreshold(polyImg,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,3,2)

## Sobel/Scharr
sobelx = cv2.Sobel(polyImg,cv2.CV_64F,1,0,ksize=-1)
sobely = cv2.Sobel(polyImg,cv2.CV_64F,0,1,ksize=-1)
 
sobel = sobelx*sobelx+sobely*sobely
mini,maxi = cv2.minMaxLoc(sobel)[:2]
sobel = (sobel * (255/maxi)).astype('uint8')

display(sobel)

pathImg = intersect(sobel,binImg).astype('uint8')
display(pathImg)

## gaussian
#gauss = cv2.GaussianBlur(polyImg,(3,3),0)

## sharpen
# kernel_sharpen_1 = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
# kernel_sharpen_2 = np.array([[1,1,1], [1,-7,1], [1,1,1]])
# kernel_sharpen_3 = np.array([[-1,-1,-1,-1,-1],
#                              [-1,2,2,2,-1],
#                              [-1,2,8,2,-1],
#                              [-1,2,2,2,-1],
#                              [-1,-1,-1,-1,-1]]) / 8.0

# output_1 = cv2.filter2D(polyImg, -1, kernel_sharpen_1)
# output_2 = cv2.filter2D(polyImg, -1, kernel_sharpen_2)
# output_3 = cv2.filter2D(polyImg, -1, kernel_sharpen_3)

# output(output_1)
# output(output_2)
# output(output_3)

## laplacian
# laplace = cv2.Laplacian(polyImg,cv2.CV_32F,ksize=1, delta = 0)
# laplace = cv2.Laplacian(polyImg,cv2.CV_32F,ksize=1, delta = 0)
# mini,maxi = cv2.minMaxLoc(laplace)[:2]
# nonzero = laplace[laplace > 0]
# mid = np.median(nonzero)
# # sigma = 1-4.0*mid/maxi
# sigma = mid/maxi
# (thresh, pathImg) = cv2.threshold(laplace,sigma*maxi+(1-sigma)*mid, 255, cv2.THRESH_BINARY)

# print str(mini) +" "+ str(mid)+" "+str(maxi)
# print sigma
# display(laplace,"Laplacian")
# display(pathImg,"Path")
############################################################################

orders = open("../orders/orders.txt", 'w')
orders.write('\n')
orders.close()

############################################################################
############################################################################
############################################################################


print "Done"
