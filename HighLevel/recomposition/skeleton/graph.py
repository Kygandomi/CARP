import cv2
import numpy as np
import bisect
import itertools
import math

from common.util import *

class graph():

	def __init__(self,point_list,autoBuild=True):
		point_list.sort()
		self.point_list = point_list
		self.size = len(point_list)
		self.node_list = []
		for i in range(self.size):
			point = self.point_list[i]
			n = node(i,point)
			self.node_list.append(n)
		if autoBuild:
			self.build()
		
	def build(self,kernel = circleKernel(3,-1),sort=True):
		hood = getNeighborPoints((0,0),kernel,sort)
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

	def clearAll(self):
		for n in self.node_list:
			n.clearAll()


class node():
	Clear, Frontier, Visited, Path, Dead, End = range(6)

	def __init__(self,index,point):
		self.index = index
		self.point = point
		self.neighbors = []

		self.parent = -1
		self.children = []
		self.status = self.Clear
		self.lowest_cost = -1

	def clearAll(self):
		self.clearCost()
		self.clearParent()
		self.clearChildren()
		self.clearCost()

	def clearCost(self):
		self.lowest_cost = -1

	def clearParent(self):
		self.parent = -1

	def clearChildren(self):
		self.children = []

	def clearStatus(self):
		self.status = self.Clear


def findPaths(graph_instance):
	def cost(from_node,to_node):
		return ((from_node.point[0]-to_node.point[0])**2+(from_node.point[1]-to_node.point[1])**2)

	def createPath(end_node):
		end_node.status = node.End
		i_original = end_node.index
		while end_node.parent != -1:
			if end_node.status == node.End:
				if end_node.index!=i_original:
					# print "Unexpected End"
					#parent.children.append(end_node.index)
					return
			#if you encounter another path, create a new endpoint and finish
			elif end_node.status == node.Path:
				end_node.status = node.End
				# print "Encountered Path"
				#parent.children.append(end_node.index)
				return
			#ensure current node is marked as path
			else: #elif end_node.status!=node.Dead:
				end_node.status = node.Path
			#if on path but not an endpoint, kill neighboring pixels
			if end_node.status == node.Path:
				for i in end_node.neighbors:
					if i==end_node.parent:
						continue
					child = graph_instance.getNode(i)
					if not (child.status == node.Path or child.status == node.End):
						#Ensure parent of each "dead" node is the closest path node
						if child.status == node.Dead:
							current_cost = cost(graph_instance.getNode(child.parent),child)
							other_cost = cost(end_node,child)
							if current_cost>other_cost:
								child.parent = end_node.index
						else:
							child.status = node.Dead
							child.parent = end_node.index

			#make this node a child of its parent
			parent = graph_instance.getNode(end_node.parent)
			parent.children.append(end_node.index)
			end_node = parent
		end_node.status = node.End
		# print "Expected End"

	def pickChild(middle_node):
		n_children = len(middle_node.children)
		if n_children == 1:
			return middle_node.children[0]
		if n_children == 0:
			return -1
		if (middle_node.parent == -1) and (n_children > 0):
			return middle_node.children[0]

		angles_list = []

		parent = graph_instance.getNode(middle_node.parent)
		delta = (parent.point[0] - middle_node.point[0],parent.point[1] - middle_node.point[1])
		angle = math.atan2(delta[1],delta[0])
		angles_list.append((parent.index,angle))

		for child_i in middle_node.children:
			child = graph_instance.getNode(child_i)
			delta = (child.point[0] - middle_node.point[0],child.point[1] - middle_node.point[1])
			angle = math.atan2(delta[1],delta[0])
			angles_list.append((child_i,angle))

		while len(angles_list) > 1:
			combos = itertools.combinations(angles_list,2)
			best_diff = -1
			best_pair = (-1,-1)
			for pair in combos:
				diff = math.pi-abs(pair[0][1] - pair[1][1])
				if best_diff == -1 or best_diff>diff:
					best_diff = diff
					best_pair = pair
			if best_pair[0][0] == parent.index:
				return best_pair[1][0]
			if best_pair[1][0] == parent.index:
				return best_pair[0][0]
			angles_list.remove(best_pair[0])
			angles_list.remove(best_pair[1])
		return -1

	#Ensure graph is in a fresh state
	graph_instance.clearAll()

	frontier_list = []

	graph_instance.clearAll()

	for n_start in graph_instance.node_list:
		#If clear, start a new frontier-based search
		if n_start.status == node.Clear:
			n_start.status = node.Frontier
			frontier_list.append(n_start)
		#If visited but not already on a path, check for endpoint and make a path
		if n_start.status == node.Visited:
			for i in n_start.neighbors:
				child = graph_instance.getNode(i)
				if child.status == node.End and n_start.parent!= child.index:
					child.parent = n_start.index
					createPath(child)
		#Explore the frontier
		while len(frontier_list) !=0:
			parent = frontier_list.pop(0)
			if parent.status==node.Frontier:
				allVisited = True
				for i in parent.neighbors:
					child = graph_instance.getNode(i)
					if child.status == node.Clear or child.status == node.Frontier:
						allVisited = False
					if child.status == node.Clear:
						child.status = child.Frontier
						frontier_list.append(child)
						child.parent = parent.index
				parent.status = node.Visited
				if allVisited:
					createPath(parent)
			# elif parent.status == node.Dead:
			# 	for i in parent.neighbors:
			# 		child = graph_instance.getNode(i)
			# 		if child.status == node.Clear:
			# 			child.status = child.Frontier
			# 			frontier_list.append(child)
			# 			child.parent = parent.index
	#At this point, graph contains endpoints, paths, and dead pixels
	

	paths = []
	#	Extract ordered lists of points from graph
	for i_start in range(graph_instance.size):
		n_start = graph_instance.getNode(i_start)
		if n_start.status == node.End:
			while len(n_start.children)!=0:
				path = [n_start.point]
				n_end = n_start
				while len(n_end.children)!=0:
					#Choose which child to use. Prioritize straight lines over sharp turns
					child_i = pickChild(n_end)
					if child_i == -1:
						paths.append(path)
						path = [n_end.point]
						child_i = n_end.children[0]
					n_end.children.remove(child_i)
					n_end = graph_instance.getNode(child_i)
					path.append(n_end.point)
				paths.append(path)

	#TODO: 
	#	Simplify graph by removing redundant endpoints and empty paths
	#		Will sometimes require reversing direction of travel

	cleanPaths = []

	for path_i in range(len(paths)):
		if path_i>=len(paths):
				break
		path = paths[path_i]
		if len(path) == 0:
			continue
		for path_j in range(path_i+1,len(paths),1):
			if path_j>=len(paths):
				break

			i_start = path[0]
			i_end = path[-1]

			path2 = paths[path_j]
			j_start = path2[0]
			j_end = path2[-1]

			if i_end == j_start:
				del path2[0]
				path.extend(path2)
				del paths[path_j]
			elif j_end == i_start:
				del path[0]
				path2.extend(path)
				path = path2
				del paths[path_j]
			elif i_end == j_end:
				del path2[-1]
				path2.reverse()
				path.extend(path2)
				del paths[path_j]
			elif i_start == j_start:
				del path2[0]
				path2.reverse()
				path2.extend(path)
				path = path2
				del paths[path_j]

		cleanPaths.append(path)

	return cleanPaths