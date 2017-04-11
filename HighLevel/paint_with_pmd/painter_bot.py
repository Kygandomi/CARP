# Import dependencies
import math
from time import sleep

import ethernet_communication as eth_comm
import paint_orders as PaintOrders
from camera.CanvasCamera import Camera
from decomposition.decomp_color.decomp_color import *
from recomposition.medialAxis.iterativeBlendedRecompose import *

from common import util

'''This class handles painting routines with arduino low level'''
class painter_bot():

	def __init__(self):
		self.desiredImg = None

		self.segmentedImg = None
		self.binImages = []
		self.colors = []
		self.indeces = []

		self.LLT_img =None
		self.listLLT = []

		self.com_obj = None
		self.painter = None
		self.camera = None
		
	def selectImage(self,fileName,path = ""):
		self.desiredImg = util.readImage(fileName, path)

		self.segmentedImg = None
		self.binImages = []

	def connect_camera(self,indeces):
		cam = Camera(indeces)

		# TODO: If you can't connect to camera, assume canvas shape is 8.5x11 starting at 0,0
		if not cam.isOpened():
			raise Exception('Could not connect to Camera')
			return False
		self.camera = cam
		return True

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
		segmented_image, color_segments, colors, indeces = decompose(desiredImg, pallete,n_colors,canvas_color=canvas_color)
		self.segmentedImg = segmented_image
		self.binImages = color_segments
		self.colors = colors
		self.indeces = indeces

		self.LLT_img = None
		self.listLLT = []

	def recompose(self,brush_size,open_images = True):
		self.LLT_img=255*np.ones(self.segmentedImg.shape,dtype='uint8')
		self.listLLT = []

		for index in range(len(self.colors)):
			img = self.binImages[index]

			if open_images: 
				img = util.open_image(img, kernel_radius = 3)

			recomposer = iterativeBlendedRecomposer(img,[brush_size])
			LLT = recomposer.recompose()

			if len(LLT)>0:
				LLT = util.arrangeLLT(LLT)
				self.LLT_img = drawLLT(LLT,self.LLT_img,thickness=brush_size,color = self.colors[index])
				LLT = cam.canvas_to_gantry(LLT)

			self.listLLT.append(LLT)

	def runPaintRoutine(self):
		self.painter.paintMulti(self.listLLT,self.indeces)