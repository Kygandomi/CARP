
import cv2
import numpy as np
import bisect

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
	# print kernal
	shape = kernal.shape
	anchor = (int(shape[0]/2),int(shape[1]/2))
	points = []
	for c in range(shape[0]):
		for r in range(shape[1]):
			if(kernal[c][r] !=0):
				if (not excludeSelf) or (not (anchor[0]==c and anchor[1]==r)) :
					points.append([pt[0]+c-anchor[0],pt[1]+r-anchor[1]])
	return np.array(points)

class graph():

	def __init__(self,point_list,autoBuild=True):
		point_list.sort()
		self.point_list = point_list
		self.size = len(point_list)
		self.node_list = []
		for i in range(self.size):
			n = node(self.getIndex(self.point_list[i]))
			self.node_list.append(n)
		if autoBuild:
			self.build()
		
	def build(self,kernal = circleKernal(3,1)):
		hood = getNeighborPoints((0,0),kernal)
		for i in range(self.size):
			n = self.node_list[i]
			n.neighbors = self.getIndeces(hood+self.getPoint(i))
	
	def getIndeces(self,points_list):
		i_list = []
		for i in range(len(points_list)):
			n_index = self.getIndex(tuple(points_list[i]))
			if n_index != -1:
				i_list.append(n_index)
		return i_list

	def getIndex(self,point):
		i = bisect.bisect_left(self.point_list, point)
		if i != self.size and self.point_list[i] == point:
			return i
		return -1

	def getPoint(self,index):
		return self.point_list[index]

	def getNode(self,index):
		return self.node_list[index]


class node():

	def __init__(self,index):
		self.index = index
		self.neighbors = []
		self.parent = -1
		self.children = []