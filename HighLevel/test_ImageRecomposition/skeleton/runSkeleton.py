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

def circleKernal(radius,thickness = -1):
	brush = cv2.circle(np.zeros((radius*2+1,radius*2+1)),(radius,radius),radius,1,thickness).astype('uint8')
	return brush

def getPoints(img,color=255):
	pts = np.where(img == 255)
	real_pts = []
	for j in range(len(pts[0])):
		real_pts.append((pts[0][j],pts[1][j]))
	return real_pts

def getNeighborPoints(pt,kernal = np.ones((3,3)),excludeSelf = True):
	print kernal
	shape = kernal.shape
	anchor = (int(shape[0]/2),int(shape[1]/2))
	points = []
	for c in range(shape[0]):
		for r in range(shape[1]):
			if(kernal[c][r] !=0):
				if (not excludeSelf) or (not (anchor[0]==c and anchor[1]==r)) :
					points.append([pt[0]+c-anchor[0],pt[1]+r-anchor[1]])
	return np.array(points)

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

def draw(pts,img,thicnkess=3): 
	'''this is what this does'''
	for i in range(len(pts)):
		if len(pts[i])==1:
			cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),0,thicnkess*3)
		else:
			for c in range(len(pts[i])-1):
				cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),0,thicnkess)

	return img

def skeletonize(binImg):
	element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
	#element = circleKernal(1)
	done = False

	img = 255-binImg.copy()
	skel = np.zeros(img.shape,np.uint8)

	while( not done):
		eroded = cv2.erode(img,element)
		temp = cv2.dilate(eroded,element)
		temp = cv2.subtract(img,temp)
		skel = cv2.bitwise_or(skel,temp)
		img = eroded.copy()

		nonzero = cv2.countNonZero(img)
		if nonzero==0:
			done = True

	return skel

############################################################################
############################################################################
############################################################################
	
desiredImg = cv2.imread('../images/cat.png', cv2.IMREAD_UNCHANGED)
brush_thickness = 2

paper_size = (11*25.4,8.5*25.4)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)

desired_rows, desired_cols = desiredImg_grey.shape

(thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
#binImg = autoCanny(desiredImg)

display(binImg)
pathImg = skeletonize(binImg)

display(pathImg)

## Remove points that do not have enough neighbors
radius = 3
border = -1
n_limit = 1
neighbors = getNeighborPoints([0,0],circleKernal(radius,border))
pts = getPoints(pathImg,255)
for point in pts:
	if pathImg[point] != 0:
		if np.count_nonzero(pathImg[neighbors[:,0]+point[0],neighbors[:,1]+point[1]]) <= n_limit:
			pathImg[point]=0

display(pathImg)


## Hough Lines Transform. Find lines on path
# minLineLength = 3
# maxLineGap = 1
# lines = cv2.HoughLinesP(pathImg,1,np.pi/180,1,minLineLength,maxLineGap)

# linesImg = cv2.cvtColor(pathImg,cv2.COLOR_GRAY2BGR)

# for x in range(0, len(lines)):
#     for x1,y1,x2,y2 in lines[x]:
#         cv2.line(linesImg,(x1,y1),(x2,y2),(0,255,0),2)

# display(linesImg)



# orders = open("../orders/orders.txt", 'w')

# n_points = 0
# out_pts = []
# for cnt_i in range(len(contours)):
# 	cnt = contours[cnt_i]
# 	list_pts=[]
# 	for pt_i in range(0,len(cnt),15):
# 		pt=cnt[pt_i][0]

# 		#pt=(8.5*25.4/1000)*pt
# 		pt=map(pt,desiredImg.shape[:2],paper_size)

# 		orders.write(str(pt[0]) + ' '+ str(pt[1]) + '\n')

# 		list_pts.append(pt)

# 		n_points = n_points + 1
# 	out_pts.append(list_pts)
# 	orders.write('\n')
# orders.close()
# print n_points

# drawnImg = draw(out_pts,np.array(255*np.ones((int(paper_size[0]),int(paper_size[1]))),dtype='uint8'),2)

# output(drawnImg, 'outImg')

print "Done"
