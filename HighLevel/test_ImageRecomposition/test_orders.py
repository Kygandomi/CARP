import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import numpy as np
import cv2
import random

def display(img, name=""):
	cv2.imshow(name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def save(img, name="output"):
	cv2.imwrite(name+".png", img)

def output(img,name="output"):
	save(img,name)
	display(img,name)

def map(pt,src_shape,dst_shape = (8.5*25.4,11*25.4),orient=True,stretch = False):
	src_rows, src_cols = src_shape
	dst_rows, dst_cols = dst_shape

	if orient:
		if (dst_rows/dst_cols>1) and (src_rows/src_cols<1):
			pt = (pt[1],src_cols-pt[0])
			src_cols, src_rows = src_shape
		elif(dst_rows/dst_cols<1) and (src_rows/src_cols>1):
			pt = (src_rows-pt[1],pt[0])
			src_cols, src_rows = src_shape

	if stretch:
		pt_new = (pt[0]*dst_cols/src_cols,pt[1]*dst_rows/src_rows)
	else:
		scale = min(min(dst_rows,dst_cols)/min(src_rows,src_cols),max(dst_rows,dst_cols)/max(src_rows,src_cols))
		offset = ((dst_cols-scale*src_cols)/2,(dst_rows-scale*src_rows)/2)
		pt_new = (scale*pt[0]+offset[0],scale*pt[1]+offset[1])
	
	return pt_new

def drawLines(pts,img,thicnkess=3):
	for i in range(len(pts)):
		if len(pts[i])==1:
			cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),0,thicnkess*3)
		else:
			for c in range(len(pts[i])-1):
				cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),0,thicnkess)

	return img

############################################################################
############################################################################
############################################################################
	
paper_size = (11*25.4,8.5*25.4)
scale = 3

fname = "erosion/orders_flower.txt"

in_pts = []
with open(fname) as f:
	# For each line in the file
	contour = []
	for line in f:
		if(line == '\n'):
			in_pts.append(contour)
			contour = []
		else:
			coords = line.split(" ")
			contour.append((scale*float(coords[0]),scale*float(coords[1])))
# print n_points

drawnImg = drawLines(in_pts,np.array(255*np.ones((int(paper_size[0]*scale),int(paper_size[1]*scale))),dtype='uint8'),2)
display(drawnImg, 'outImg')

print "Done"
