
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
			if(kernal[c][r] != 0):
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


# def explore(graph_instance):
# 	'''TODO: returns endpoints of the graph'''
# 	frontier_list = []
# 	endpoints = []
# 	i_segment = -1

# 	graph_instance.clearAll()

# 	for n_start in graph_instance.node_list:
# 		if n_start.status == node.Clear:
# 			endpoints.append([])
# 			i_segment += 1
# 			n_start.status = node.Frontier
# 			frontier_list.append(n_start)
# 			endpoints[i_segment].append(n_start)
# 		while len(frontier_list) !=0:
# 			parent = frontier_list.pop(0)
# 			allVisited = True
# 			for i in parent.neighbors:
# 				child = graph_instance.getNode(i)
# 				if child.status == node.Clear or child.status == node.Frontier:
# 					allVisited = False
# 				if child.status == node.Clear:
# 					child.status = child.Frontier
# 					frontier_list.append(child)
# 			parent.status = node.Visited
# 			if allVisited:
# 				endpoints[i_segment].append(parent)

# 	return endpoints

# def a_star(graph_instance,start_node,end_node):
# 	def heuristic(from_node,to_node):
# 		return ((from_node.point[0]-to_node.point[0])**2+(from_node.point[1]-to_node.point[1])**2)

# 	def cost(from_node,to_node):
# 		return heuristic(from_node,to_node)

# 	for node_instance in graph_instance.node_list:
# 		node_instance.clearCost()
# 		if node_instance.status != node.Path and node_instance.status != node.Dead and node_instance.status != node.Endpoint:
# 			node_instance.clearAll()

# 	#list = [(cost+heuristic,node),(..,..)......]

# 	start_node.lowest_cost = 0
# 	frontier_list = [(heuristic(start_node,end_node),start_node)]
# 	while len(frontier_list) != 0:
# 		parent = frontier_list.pop(0)[1]
# 		for child_i in parent.neighbors:
# 			child = graph_instance.getNode(child_i)
# 			if child.status == node.Dead:
# 				continue

# 			#Check if already on a path
# 			#Check for endpoints
			
# 			c = cost(parent,child)
# 			c_total = parent.lowest_cost+c
# 			if child.lowest_cost <0 or c_total<child.lowest_cost:
# 				child.lowest_cost = c_total
# 				child.parent = parent.index

# 				#Check for goal reached
# 				if child.index == end_node.index:
# 					return child

# 				h = heuristic(child,end_node)
# 				frontier_list.append(((c_total+h),child))
# 				frontier_list.sort()

# 	# No Path found to end. Find node with max lowest_cost and return it
# 	max_node = start_node
# 	for n in graph_instance.node_list:
# 		if n.lowest_cost>max_node.lowest_cost:
# 			max_node = n
# 	return max_node

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
					return
			#if you encounter another path, create a new endpoint and finish
			elif end_node.status == node.Path:
				end_node.status = node.End
				# print "Encountered Path"
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

	# def reverse(end_node,start_node = None):
	# 	n_kids = len(end_node.children) == 0:
	# 	if end_node.parent == -1:
	# 		if n_kids == 0:
	# 			print "Can't reverse: No connections"
	# 			return False
	# 		elif n_kids == 1:
	# 			end_node.parent = end_node.children.pop(0)
	# 			return True
	# 		elif start_node is not None and (start_node.index in end_node.children):
	# 			end_node.children.remove(start_node.index)
	# 			end_node.parent = start_node.index
	# 			return True
	# 		else
	# 			print "Can't reverse: too many kids and no parent"
	# 			return False
	# 	else:
	# 		if n_kids == 0:
	# 			end_node.children.append(end_node.parent)
	# 			end_node.clearParent()
	# 			return True
	# 		elif n_kids == 1:
	# 			if reverse(graph_instance.getNode(end_node.parent),end_node)
	# 				end_node.children.append(end_node.parent)
	# 				end_node.parent = end_node.children.pop(0)
	# 				return True
	# 		elif start_node is not None and (start_node.index in end_node.children):
	# 			end_node.children.remove(start_node.index)
	# 			end_node.parent = start_node.index
	# 			return True

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
					child.children.append(n_start.index)
					createPath(n_start)
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

	#At this point, graph contains endpoints, paths, and dead pixels
	#TODO: 
	#	Simplify graph by removing redundant endpoints
	#		Will sometimes require reversing direction of travel

	paths = []
	#	Extract ordered lists of points from graph
	for i_start in range(graph_instance.size):
		n_start = graph_instance.getNode(i_start)
		if n_start.status == node.End:
			while len(n_start.children)!=0:
				path = []
				n_end = n_start
				while len(n_end.children)!=0:
					path.append(n_end.point)
					#TODO: make smarter decision about which child to use
					# ex: 3 children. pick one or the other or none
					n_end = graph_instance.getNode(n_end.children.pop(0))
				paths.append(path)
		if len(n_start.children)!=0:
			i_start -= 1

	return paths