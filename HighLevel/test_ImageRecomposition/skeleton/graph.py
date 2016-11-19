
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
			point = self.point_list[i]
			n = node(self.getIndex(point),point)
			self.node_list.append(n)
		if autoBuild:
			self.build()
		
	def build(self,kernal = circleKernal(3,-1)):
		print kernal
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

	def clear(self):
		for n in self.node_list:
			n.clear()


class node():
	Clear, Frontier, Visited, Path, Dead = range(5)

	def __init__(self,index,point):
		self.index = index
		self.point = point
		self.neighbors = []
		self.parent = -1
		self.children = []
		self.status = self.Clear

	def clear(self):
		self.parent = -1
		self.children = []
		self.status = self.Clear

def explore(graph_instance):
	'''TODO: returns endpoints of the graph'''
	frontier_list = []
	endpoints = []
	i_segment = -1

	for n_start in graph_instance.node_list:
		if n_start.status == node.Clear:
			endpoints.append([])
			i_segment += 1
			n_start.status = node.Frontier
			frontier_list.append(n_start)
			endpoints[i_segment].append(n_start)
		while len(frontier_list) !=0:
			parent = frontier_list.pop(0)
			allVisited = True
			for i in parent.neighbors:
				child = graph_instance.getNode(i)
				if child.status != node.Visited:
					allVisited = False
				if child.status == node.Clear:
					child.status = child.Frontier
					frontier_list.append(child)
			parent.status = node.Visited
			if allVisited:
				endpoints[i_segment].append(parent)

	return endpoints