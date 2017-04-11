# Import dependencies
import math
from time import sleep
import cv2

import ethernet_communication as eth_comm
import paint_orders as PaintOrders
from camera.CanvasCamera import Camera
from decomposition.decomp_color.decomp_color import *
from recomposition.medialAxis.iterativeBlendedRecompose import *

from common import util

'''This class handles painting routines with arduino low level'''
class painter_bot():

	def __init__(self):
		self.inputImg = None

		self.desiredImg = None

		self.segmentedImg = None
		self.binImages = []
		self.colors = []
		self.indeces = []

		self.lltImg =None
		self.lltListImg = []
		self.lltListGantry = []

		self.com_obj = None
		self.painter = None
		self.camera = None
		
	def selectImage(self,fileName,path = ""):
		self.inputImg = util.readImage(fileName, path)

		self.desiredImg = None
		self.segmentedImg = None
		self.binImages = []
		self.lltImg =None
		self.lltList = []

		if not self.camera is None:
			self.desiredImg = util.resize_with_buffer(self.desiredImg,self.camera.get_canvas())

	def connect_camera(self,indeces):
		cam = Camera(indeces)

		# TODO: If you can't connect to camera, assume canvas shape is 8.5x11 starting at 0,0
		if not cam.isOpened():
			# raise Exception('Could not connect to Camera')
			return False
		self.camera = cam
		return True

	def findCanvas():
		if self.camera is None:
			return

		self.desiredImg = None
		self.segmentedImg = None
		self.binImages = []
		self.lltImg =None
		self.lltListImg = []
		self.lltListGantry = []

		self.camera.generate_transform()
		return self.camera.get_canvas()

	def connect_eth(self,ip,port):
		pmd_com = eth_comm.ethernet_comms(ip, port)
		connected = pmd_com.connect()
		if not connected:
			raise Exception('Could not connect via Ethernet')
			return False
		# Sleep to verify a solid connection
		sleep(0.1)
		self.com_obj = pmd_com
		self.painter = PaintOrders.paint_orders(pmd_com)
		return True

	def decompose(self,n_colors,pallete = [],canvas_color=[255,255,255]):
		if self.desiredImg is None:
			return
		segmented_image, color_segments, colors, indeces = decompose(desiredImg, pallete,n_colors,canvas_color=canvas_color)
		self.segmentedImg = segmented_image
		self.binImages = color_segments
		self.colors = colors
		self.indeces = indeces

		self.lltImg = None
		self.lltListImg = []
		self.lltListGantry = []

	def recompose(self,args,open_images = True):
		if self.segmentedImg is None or len(self.binImages)==0:
			return

		self.lltListImg = self.recompose_helper(self.binImages,args,open_images)
		self.lltImg = self.makeImgLLT(self.segmentedImg.shape,self.lltListImg,self.colors,args[0])
		self.lltListGantry = []

	def paint(self):
		self.lltListGantry = self.mapToGantry(self.lltListImg,self.camera)
		self.painter.paintMulti(self.lltListGantry,self.indeces)

	def paint_with_feedback(self,args,open_images,max_iter = 4):
		if self.segmentedImg is None or len(self.binImages)==0:
			return

		if len(self.binImages)==0:
			self.recompose(args,open_images)

		for i in range(len(max_iter)):
			# Get a canvas image
			painting = self.camera.get_canvas()

			# Segment the canvas image
			segmented_image_act, color_segments_act, paint_colors, pallete_indeces = decompose(painting, self.colors,self.n_colors,canvas_color=self.canvas_color)

			# Generate corrections for canvas image
			correction_segments, canvas_corrections = cam.correct_image(self.binImages,color_segments_act)

			lltListImg = self.recompose_helper(correction_segments,args,open_images)
			lltListGantry = self.mapToGantry(lltListImg)
			self.painter.paintMulti(lltListGantry,self.indeces)

	####### HELPERS #######

	def mapToGantry(self,lltListImg,cam):
		lltListGantry = []
		for LLT in lltListImg:
			lltListGantry.append(cam.canvas_to_gantry(LLT))
		return lltListGantry

	def recompose_helper(self,binImages,args,open_images = True):
		listLLT = []
		for index in range(len(binImages)):
			img = binImages[index]

			if open_images: 
				img = util.open_image(img, kernel_radius = 3)

			recomposer = iterativeBlendedRecomposer(img,args)
			LLT = recomposer.recompose()

			if len(LLT)>0:
				LLT = util.arrangeLLT(LLT)
			listLLT.append(LLT)
		return listLLT

	def makeImgLLT(self,img_shape,lltListImg,colors,thickness = 1):
		img = 255*np.ones(img_shape,dtype='uint8')
		for i in range(len(colors)):
			img = drawLLT(lltListImg[i],img,thickness=thickness,color = colors[i])
		return img
