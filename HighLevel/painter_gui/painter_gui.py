#! /usr/bin/env python
# CARP MQP -- Painting GUI

#Import Dependencies
import wx
import os 
import sys
import user
import cv2
import numpy as np
import wx.grid as gridlib
from wx.lib.masked import NumCtrl
from common.util import *
from recomposition.recomp_funcs import *
from paint_with_pmd.painter_bot import *
import PIL

from time import sleep

class PainterGUI(wx.Frame):

	def __init__(self): 
		# Initialize WX Frame
		wx.Frame.__init__(self, None, wx.ID_ANY,"CARP MQP User Interface",size=(680,600))

		# Create Size Object -- responsible for page layout
		self.sizer = wx.BoxSizer(wx.VERTICAL)

		# Create the major panels of the application
		self.panel_one = PanelOne(self)
		
		# Hide all frames except the welcome screen
		self.panel_one.Show()
		
		# Put everyting on the frame
		self.sizer.Add(self.panel_one, 1, wx.EXPAND)
		self.SetSizer(self.sizer)

		# Create the application menu bar at the top of the screen
		menubar = wx.MenuBar()
		self.fileMenu = wx.Menu()
		self.fileMenu.Append(1, "&Open", "Open from file..")
		self.fileMenu.AppendSeparator()
		self.fileMenu.Append(2, "&Close", "Quit")

		# Bind events to application menu
		self.Bind(wx.EVT_MENU, self.panel_one.onSelectFile, id=1)
		self.Bind(wx.EVT_MENU, self.onExit, id=2)
		menubar.Append(self.fileMenu, '&File')
		self.SetMenuBar(menubar)
		self.Bind(wx.EVT_CLOSE, self.onExit)

	# Method for closing the application
	def onExit(self, evt):
		self.Destroy()

'Welcome Screen Panel -- First Panel shown in the application'
class PanelOne(wx.Panel):

	def __init__(self, parent):
		self.bot = painter_bot()
		self.bot.connect_camera([1,0])
		# Initialize Welcome Screen
		wx.Panel.__init__(self, parent=parent)

		####################  Welcome Screen Text ################### 
		font1 = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		txt = wx.StaticText(self, label="Welcome to CARP MQP Painter Application", pos=(20, 10))
		txt.SetFont(font1)
		self.txt2 = wx.StaticText(self, label="Please select an image to process", pos=(20, 45))

		# Button For selecting a Video File
		button = wx.Button(self, label="Choose Image...", pos=(20, 70))
		button.Bind(wx.EVT_BUTTON, self.onSelectFile)

		# Button for Going to the next panel -- Disabled until a video file has been chosen
		self.paint_button =wx.Button(self, label="Paint", pos=(150, 70))
		self.paint_button.Bind(wx.EVT_BUTTON, self.paint)
		self.paint_button.Disable()

		# Variable for central image
		self.main_image = ''

		# Place Image of CARP logo
		png = wx.Image('./painter_gui/carp.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		wx.StaticBitmap(self, -1, png, (530, 5), (120,120))

		################### Decomposition Section ################### 
		CONTROLS_OFFSET_LEFT = 450
		DY = 110
		
		txt3 = wx.StaticText(self, label="Decomposition", pos=(CONTROLS_OFFSET_LEFT, DY))
		self.MAX_COLORS = 6
		
		txt31 = wx.StaticText(self, label="# of Colors: ", pos=(CONTROLS_OFFSET_LEFT, DY+23))
		# self.decomp_num_colors = wx.TextCtrl(self, value=self.num_colors, pos=(CONTROLS_OFFSET_LEFT, 150))
		self.decomp_num_colors = NumCtrl(self, value=self.MAX_COLORS,size=(40,20),pos=(CONTROLS_OFFSET_LEFT+70, DY+20),integerWidth = 2,limitOnFieldChange = True,min = 0, max = self.MAX_COLORS)

		self.auto_colors_button = wx.Button(self, label="Auto", pos=(CONTROLS_OFFSET_LEFT+110, DY+19))
		self.auto_colors_button.Bind(wx.EVT_BUTTON, lambda evt,var=False: self.decomp(evt,var))

		self.color_data = wx.ColourData()
		self.color_data.SetChooseFull(True)

		self.paint_colors = []
		
		# wx.ColourDialog(self, data=None)
		for i in range(self.MAX_COLORS):
			panel = wx.Panel(self,name="color "+str(i+1),pos=(CONTROLS_OFFSET_LEFT+30*i, DY+50),style=wx.SIMPLE_BORDER)
			panel.BackgroundColour = wx.WHITE

			panel.Bind(wx.EVT_LEFT_UP, lambda evt,index=i: self.pickColor(index))
			self.paint_colors.append(panel)

		panel = wx.Panel(self,name="color "+str(self.MAX_COLORS+1),pos=(CONTROLS_OFFSET_LEFT+90, DY+80),style=wx.SIMPLE_BORDER)
		panel.BackgroundColour = wx.WHITE
		panel.Bind(wx.EVT_LEFT_UP, lambda evt,index=self.MAX_COLORS: self.pickColor(self.MAX_COLORS))
		self.paint_colors.append(panel)

		self.canvas_checkbox = wx.CheckBox(self, label="Canvas:", pos=(CONTROLS_OFFSET_LEFT+20, DY+82))
		self.canvas_checkbox.SetValue(True)
		self.canvas_checkbox.Bind(wx.EVT_CHECKBOX, lambda evt,index=self.MAX_COLORS: self.paint_colors[self.MAX_COLORS].Show(self.canvas_checkbox.GetValue()))

		self.decomp_button_apply = wx.Button(self, label="Apply", pos=(CONTROLS_OFFSET_LEFT, DY+110))
		self.decomp_button_apply.Bind(wx.EVT_BUTTON, self.decomp)

		self.disable_decomp()

		####################  Recomposition Section ################### 
		RY = 260

		txt4 = wx.StaticText(self, label="Recomposition", pos=(CONTROLS_OFFSET_LEFT, RY))
		txt5 = wx.StaticText(self, label="Select a Recomposition Method", pos=(CONTROLS_OFFSET_LEFT, RY+20))

		self.rb1 = wx.RadioButton(self, 11, label = 'Iterative Erosion', pos = (CONTROLS_OFFSET_LEFT, RY+50), style = wx.RB_GROUP) 
		self.rb2 = wx.RadioButton(self, 22, label = 'Skeleton',pos = (CONTROLS_OFFSET_LEFT, RY+70)) 
		self.rb3 = wx.RadioButton(self, 33, label = 'Blended Recomposition',pos = (CONTROLS_OFFSET_LEFT, RY+90))

		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb1.GetId())
		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb2.GetId())
		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb3.GetId())

		txt31 = wx.StaticText(self, label="Brush Radius: ", pos=(CONTROLS_OFFSET_LEFT, RY+123))
		self.recomp_brush_radius = NumCtrl(self, value=4,pos=(CONTROLS_OFFSET_LEFT+80, RY+120),integerWidth = 2,limitOnFieldChange = True,min = 1, max = 99)

		self.recomp_button_apply = wx.Button(self, label="Apply", pos=(CONTROLS_OFFSET_LEFT, RY+150))
		self.recomp_button_apply.Bind(wx.EVT_BUTTON, self.recomp)
		
		self.disable_recomp()

	def disable_decomp(self):
		self.enable_decomp(False)

	def enable_decomp(self,value=True):
		self.decomp_num_colors.Enable(value)
		self.decomp_button_apply.Enable(value)
		self.auto_colors_button.Enable(value)
		for box in self.paint_colors:
			box.Enable(value)
		self.canvas_checkbox.Enable(value)

	def disable_recomp(self):
		self.enable_recomp(False)

	def enable_recomp(self,value=True):
		self.rb1.Enable(value)
		self.rb2.Enable(value)
		self.rb3.Enable(value)
		self.recomp_button_apply.Enable(value)
		self.recomp_brush_radius.Enable(value)

	def enable_paint(self,value=True):
		self.paint_button.Enable(value)

	def disable_paint(self):
		self.enable_paint(False)

	def pickColor(self,index):
		print "pick ",index
		# set the default color in the chooser
		self.color_data.SetColour(self.paint_colors[index].GetBackgroundColour())

		# construct the chooser
		dlg = wx.ColourDialog(self, self.color_data)

		if dlg.ShowModal() == wx.ID_OK:
			# set the panel background color
			self.color_data = dlg.GetColourData()
			color = dlg.GetColourData().Colour
			# self.bot.colors[index] = [color.Blue,color.Green,color.Red]
			self.paint_colors[index].SetBackgroundColour(color)
		dlg.Destroy()

		self.Refresh()

	def SetVal(self, event):
		state1 = str(self.rb1.GetValue())
		state2 = str(self.rb2.GetValue())
		state3 = str(self.rb3.GetValue())

		print "state1 ", state1 
		print "state2 ", state2 
		print "state3 ", state3 

	# Method for calling function to paint
	def paint(self,event):
		print "Paint"

		self.bot.connect_eth(ip = '192.168.178.7',port = 1234)
		self.bot.paint()
		# bot.paint_with_feedback([4])

	# Method for performing decomp
	def decomp(self,event,usePallete=True):
		print "Decomp"

		self.disable_decomp()
		self.disable_recomp()
		self.disable_paint()

		pallete = []
		num_colors = self.decomp_num_colors.GetValue()

		if usePallete:
			for i in range(num_colors):
				color = self.paint_colors[i].GetBackgroundColour()
				pallete.append([int(color.Blue()),int(color.Green()),int(color.Red())])
			num_colors = 0

		canvas_color = None
		if self.canvas_checkbox.GetValue():
			color = self.paint_colors[self.MAX_COLORS].GetBackgroundColour()
			canvas_color = [int(color.Blue()),int(color.Green()),int(color.Red())]

		self.bot.decompose(num_colors,pallete,canvas_color)

		for i in range(len(self.bot.colors)):
			color = self.bot.colors[i]
			self.paint_colors[i].BackgroundColour = wx.Colour(color[2],color[1],color[0])
			self.color_data.SetCustomColour(15-i, wx.Colour(color[2],color[1],color[0]))
		i=i+1
		if i<len(self.paint_colors):
			for j in range(i,len(self.paint_colors)):
				self.paint_colors[j].BackgroundColour = wx.Colour(255,255,255)


		self.setImage(self.bot.segmentedImg)

		self.enable_decomp()
		self.enable_recomp()
		self.disable_paint()

	# Method for performing recomp
	def recomp(self,event):
		print "Recomp"
		self.disable_recomp()

		radius = self.recomp_brush_radius.GetValue()

		re_func = None

		if self.rb1.GetValue():
			re_func = iterativeErosionRecomp
		elif self.rb2.GetValue():
			re_func = medialAxisRecomp
		elif self.rb3.GetValue():
			re_func = iterativeBlendedRecomp

		self.bot.recompose([radius],recomp_fun = re_func,open_images = True)
		self.setImage(self.bot.lltImg)

		self.enable_recomp()
		self.enable_paint()

	def scale_bitmap(self, bitmap, width, height):
	    image = wx.ImageFromBitmap(bitmap)
	    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
	    result = wx.BitmapFromImage(image)
	    return result

	def setImage(self,input_image):
		ideal = np.zeros([400, 400, 3])
		resized_image = resize_with_buffer(input_image , ideal,padding_color = [0,0,0])
		cv2.imwrite('./painter_gui/resized.png', resized_image)
		self.main_image = wx.Image('./painter_gui/resized.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		wx.StaticBitmap(self, -1, self.main_image, (20, 110), (resized_image.shape[0],resized_image.shape[1]))
		self.Refresh()

    # Method for launching file dialog box
	def onSelectFile(self, event):

        # Launch Dialog Box
		dlg = wx.FileDialog(self, "Choose a file", user.home, "","*.*")
		if dlg.ShowModal() == wx.ID_OK:
			# Save selected file name and directory
		    dirname = dlg.GetDirectory()
		    filename = dlg.GetFilename()

		    # Display Image
		    input_image = readImage(filename,dirname+"/")
		    self.bot.setImage(input_image)
		    self.setImage(self.bot.desiredImg)

		    # Report file selected and enable decomp section
		    self.txt2.SetLabel("Selected file: " + filename)
		    self.enable_decomp()
		    self.disable_recomp()
		    self.disable_paint()

		    self.Refresh()

		# On Completion destroy dialog box
		dlg.Destroy()