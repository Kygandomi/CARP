import cv2
import numpy as np
import bisect
import itertools
import math

from common.util import *

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

def cost(from_node,to_node):
		return math.sqrt((from_node.point[0]-to_node.point[0])**2+(from_node.point[1]-to_node.point[1])**2)

class graph():

	def __init__(self,point_list,path_img,autoBuild=True):
		point_list.sort()
		self.point_list = point_list
		self.size = len(point_list)
		self.node_list = []
		self.max_cost = -1
		for i in range(self.size):
			point = self.point_list[i]
			n = node(i,point)
			self.node_list.append(n)
		if autoBuild:
			self.build()
		if not path_img is None:
			self.image = path_img
		
	def build(self,kernel = np.ones((3,3)),sort=True):
		hood = getNeighborPoints((0,0),kernel,sort)
		n_zero = node(0,(0,0))
		for i in range(len(hood)):
			self.max_cost = max(self.max_cost,cost(n_zero,node(1,hood[i])))
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

	def getNodes(self,index_list):
		n_list = []
		for n_index in range(len(index_list)):
			n_list.append(self.getNode(n_index))
		return n_list

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

	def clearCost(self):
		for n in self.node_list:
			n.lowest_cost = -1

	def clearParent(self):
		for n in self.node_list:
			n.parent = -1

	def clearChildren(self):
		for n in self.node_list:
			n.children = []

	def clearStatus(self):
		for n in self.node_list:
			n.status = node.Clear

def createNodeImg(pathImg, g):
        nodeImg = cv2.cvtColor(pathImg.copy(),cv2.COLOR_GRAY2BGR)
        for node in g.node_list:
            if node.status == node.End:
                nodeImg[node.point[0],node.point[1]] = (0,0,255)
            elif node.status == node.Path:
                nodeImg[node.point[0],node.point[1]] = (0,255,255)
            elif node.status == node.Dead:
                nodeImg[node.point[0],node.point[1]] = (200,200,200)
            elif node.status == node.Visited:
                nodeImg[node.point[0],node.point[1]] = (255,0,0)
            elif node.status == node.Frontier:
                nodeImg[node.point[0],node.point[1]] = (255,255,0)
        return nodeImg

def cost(from_node,to_node):
		return math.sqrt((from_node.point[0]-to_node.point[0])**2+(from_node.point[1]-to_node.point[1])**2)

def assignCosts(graph_instance):
	frontier_list = []

	def addToFrontier(node):
		node.status = node.Frontier
		frontier_list.append(node)

	def visit(parent):
		for i in parent.neighbors:
			child = graph_instance.getNode(i)
			total_dist = parent.lowest_cost+cost(parent,child)
			#Check if distance needs to be updated
			if child.lowest_cost == -1 or total_dist<child.lowest_cost:
				child.lowest_cost = total_dist
				#if not in the frontier, add to frontier
				if not (child.status == node.Frontier):
					addToFrontier(child)
				child.parent = parent.index
		parent.status = node.Visited

	for n_start in graph_instance.node_list:
		# If clear, start a new BFS
		if n_start.status == node.Clear:
			n_start.status = node.Frontier
			n_start.lowest_cost = 0
			frontier_list.append(n_start)
		# Explore the frontier using BFS
		while len(frontier_list) != 0:
			parent = frontier_list.pop(0)
			#if already visited, we dont need to do anything
			if not (parent.status == node.Visited):
				visit(parent)
	return graph_instance

def BFS(graph_instance, start_node, n=-1):
	cost_frontier_list = []
	start_cost = start_node.lowest_cost
	new_nodes = []

	def addToFrontier(node,depth):
		node.status = node.Frontier;
		cost_frontier_list.append((abs(node.lowest_cost-start_cost),node.index,depth))

	def visit(parent,depth):
		if depth==0:
			return
		for i in parent.neighbors:
			child = graph_instance.getNode(i)
			if not (child.status==node.Dead or child.status == node.Path or child.status==node.End):
				total_dist = parent.lowest_cost+cost(parent,child)
				#Check if distance needs to be updated
				if child.lowest_cost == -1 or total_dist<child.lowest_cost:
					child.lowest_cost = total_dist
					#if distance changed, add to frontier
					addToFrontier(child,max(depth-1,-1))
					if not (child.index in new_nodes):
						new_nodes.append(child.index)
					child.parent = parent.index
		parent.status = node.Visited

	cost_frontier_list.append((abs(start_node.lowest_cost-start_cost),start_node.index,n))
	while(len(cost_frontier_list)>0):
		cost_frontier_list.sort()
		_,i_parent,depth = cost_frontier_list.pop(0)
		parent = graph_instance.getNode(i_parent)
		if parent.status == node.Frontier:
			visit(parent,depth)

	# for n in frontier_nodes
	# 	if n.status == node.Frontier
	# 		frontier_nodes.append(n.index)
	return new_nodes

def findPaths(graph_instance):

	cost_frontier_list = []

	def addToFrontier(node):
		node.status = node.Frontier;
		cost_frontier_list.append((node.lowest_cost,node.index))

	# def visit(parent):
	# 	for i in parent.neighbors:
	# 		child = graph_instance.getNode(i)
	# 		total_dist = parent.lowest_cost+cost(parent,child)
	# 		#Check if distance needs to be updated
	# 		if child.lowest_cost == -1 or total_dist<child.lowest_cost:
	# 			child.lowest_cost = total_dist
	# 			#if not in the frontier, add to frontier
	# 			if not (child.status == node.Frontier):
	# 				addToFrontier(child)
	# 			child.parent = parent.index
	# 	parent.status = node.Visited

	# def createPath(end_node):
	# 	path_indeces = [end_node.index]
	# 	end_node.status = node.Dead
	# 	for i_child in end_node.neighbors:
	# 		child = graph_instance.getNode(i_child)
	# 		if not (child.index in end_node.children):
	# 			child.status = node.Dead
	# 		elif child.status != node.Path:
	# 			child.status = node.Path

	def checkEndpoint(node_instance):
		if node_instance.status == node.Dead or node_instance.status == node.Path:
			return -1

		max_diff = 0
		for i_child in node_instance.neighbors:
			child = graph_instance.getNode(i_child)
			if child.status == node.Clear or child.status == node.End:
				return -1
			# Cost is greater than all non path/deadneighbors	
			if child.status == node.Frontier or child.status == node.Visited:
				diff = node_instance.lowest_cost-child.lowest_cost
				if diff<0:
					return -1
				if diff>max_diff:
					max_diff = diff

		# if neighbor is too far away, loop detected
		if max_diff>(graph_instance.max_cost+0.1):
			#return index of the child with the lowest cost (greatest cost difference)
			next_node = node_instance
			for i_child in node_instance.neighbors:
				child = graph_instance.getNode(i_child)
				if child.lowest_cost < next_node.lowest_cost:
					next_node = child
			return next_node.index
		return node_instance.index
				
		# 	# prev_i = prev_node.index
		# 	# prev_node = next_node
		# 	# next_node = graph_instance.getNode(next_node.parent)
		# 	# prev_node.parent = prev_i
		# 	while not ((next_node.status == node.Path) or (next_node.status == node.Visited) or (next_node.status == node.End)):
		# 		print "prev ", prev_node.index, ", ", prev_node.point
		# 		print "next ", next_node.index, ", ", next_node.point
		# 		prev_i = prev_node.index
		# 		prev_node = next_node
		# 		next_node = graph_instance.getNode(next_node.parent)
		# 		prev_node.parent = prev_i
		# 	print "return other"
		# 	return next_node.index
		# else:
		# 	print "return self"
		# 	return node_instance.index

	def checkEndpoint_old(node_instance):
		if node_instance.status == node.Dead or node_instance.status == node.Path:
			return -1

		isGreatest = True
		for i_child in node_instance.neighbors:
			child = graph_instance.getNode(i_child)
			if child.status == node.Clear or child.status == node.End:
				return -1
			# Cost is greater than all non path/deadneighbors	
			if child.status== node.Frontier or child.status == node.Visited:
				if(child.lowest_cost>node_instance.lowest_cost):
					isGreatest = False

		if isGreatest:
			return self.index
		return -1

	def killNeighbors(node_instance):
		for i in node_instance.neighbors:
			if i==node_instance.parent:
				continue
			child = graph_instance.getNode(i)
			if not (child.status == node.Path or child.status == node.End):
				#Ensure parent of each "dead" node is the closest path node
				if child.status == node.Dead:
					current_cost = cost(graph_instance.getNode(child.parent),child)
					other_cost = cost(node_instance,child)
					if current_cost>other_cost:
						child.parent = node_instance.index
				else:
					child.status = node.Dead
					child.parent = node_instance.index

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
				# if this path is close to another endpoint, make this the end and that a path point
				# for i in end_node.neighbors:
				# 	child = graph_instance.getNode(i)
				# 	if child.status==node.End:
				# 		child.status=node.Path
				# 		if not end_node.index in child.children:
				# 			child.children.append(end_node.index)
				# 		end_node.parent = child.index
				return
			#ensure current node is marked as path
			else: #elif end_node.status!=node.Dead:
				end_node.status = node.Path
			#if on path but not an endpoint, kill neighboring pixels
			if end_node.status == node.Path:
				killNeighbors(end_node)

			#make this node a child of its parent
			parent = graph_instance.getNode(end_node.parent)
			if not end_node.index in parent.children:
				parent.children.append(end_node.index)
			end_node = parent
		end_node.status = node.End
		# print "Expected End"

	def extendStart(start_node,child):
		if(start_node.status!=node.End):
			return
		prev_node = start_node
		next_node = child

		while not ((next_node.status == node.Path) or (next_node.status == node.End)):
			next_i = next_node.parent
			next_node.parent = prev_node.index
			if not next_node.index in prev_node.children:
				prev_node.children.append(next_node.index)
			prev_node.status = node.Path
			killNeighbors(prev_node)
			prev_node = next_node
			next_node = graph_instance.getNode(next_i)

			# print "prev: ", prev_node.point
			# print "next: ", next_node.point
			# output(createNodeImg(graph_instance.image,graph_instance))

		next_node.parent = prev_node.index
		if not next_node.index in prev_node.children:
			prev_node.children.append(next_node.index)
		prev_node.status = node.Path
		next_node.status = node.End

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

	def extractPaths(graph_instance):
		paths = []
		#	Extract ordered lists of points from graph
		for n_start in graph_instance.node_list:
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
		return paths

	graph_instance.clearAll()

	for n_start in graph_instance.node_list:
		# If clear, start a new search
		if n_start.status == node.Clear:
			addToFrontier(n_start)
		# Explore the frontier, searching for endpoints and creating paths
		while len(cost_frontier_list) !=0:
			cost_frontier_list.sort()
			_,i_parent = cost_frontier_list.pop()
			parent = graph_instance.getNode(i_parent)
			if(parent.status == node.Frontier) or (parent.status == node.Dead):
				new_nodes = BFS(graph_instance,parent,3)
				for i_node in new_nodes:
					addToFrontier(graph_instance.getNode(i_node))

			#search for an endpoint near this node
			endpoint = checkEndpoint(parent)
			if endpoint != -1:
				createPath(graph_instance.getNode(parent.index))
				if endpoint!=parent.index:
					# Extend start of path to join with other path
					extendStart(parent,graph_instance.getNode(endpoint))

			# if not (parent.status == node.Dead or parent.status == node.Path):
			# 	output(createNodeImg(graph_instance.image,graph_instance))

	paths = extractPaths(graph_instance)
	return paths

def findPaths_old2(graph_instance):

	cost_frontier_list = []
	endpoint_list = []

	def addToFrontier(node):
		node.status = node.Frontier;
		cost_frontier_list.append((node.lowest_cost,node.index))
		cost_frontier_list.sort()

	def visit(parent):
		isGreatest = True
		for i in parent.neighbors:
			child = graph_instance.getNode(i)
			if (child.status == node.Clear):
				addToFrontier(child)
				if not parent.index in child.children:
					child.children.append(parent.index)
			#node is an endpont if its distance from start is greater than all neighbors
			if child.lowest_cost<parent.lowest_cost:
				#if node is not futher than all neighbors, then it is not definitely an endpoint
				isGreatest=False
		parent.status = node.Visited
		return isGreatest

	# def createPath(end_node):
	# 	path_indeces = [end_node.index]
	# 	end_node.status = node.Dead
	# 	for i_child in end_node.neighbors:
	# 		child = graph_instance.getNode(i_child)
	# 		if not (child.index in end_node.children):
	# 			child.status = node.Dead
	# 		elif child.status != node.Path:
	# 			child.status = node.Path


	graph_instance.clearAll()
	# Assign costs using BFS. allows us to run DFS to find critical points
	graph_instance = assignCosts(graph_instance)
	graph_instance.clearStatus()
	graph_instance.clearParent()

	for n_start in graph_instance.node_list:
		# If clear, start a new DFS
		if n_start.lowest_cost == 0:
			addToFrontier(n_start)
		# Explore the frontier using DFS, searching for endpoints
		while len(cost_frontier_list) !=0:
			_,i_parent = cost_frontier_list.pop()
			parent = graph_instance.getNode(i_parent)
			if not (parent.status == node.Visited):
				isEndpoint = visit(parent)
				if isEndpoint:
					parent.status = node.End

	return graph_instance

def findPaths_old(graph_instance):
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
				if (child.status == node.End or child.status ==node.Dead) and n_start.parent!= child.index:
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
			elif parent.status == node.Dead:
				for i in parent.neighbors:
					child = graph_instance.getNode(i)
					if child.status == node.Clear:
						child.status = child.Frontier
						frontier_list.append(child)
						child.parent = parent.index
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