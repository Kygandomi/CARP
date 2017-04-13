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
from common.util import *
import PIL

from time import sleep

# Create Global File Name and Directory for selected image
filename = ""

class PainterGUI(wx.Frame):

	def __init__(self): 
		# Initialize WX Frame
		wx.Frame.__init__(self, None, wx.ID_ANY,"CARP MQP User Interface",size=(880,500))

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
		# Initialize Welcome Screen
		wx.Panel.__init__(self, parent=parent)

		####################  Welcome Screen Text ################### 
		font1 = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		txt = wx.StaticText(self, label="Welcome to CARP MQP Painter Application", pos=(20, 30))
		txt.SetFont(font1)
		self.txt2 = wx.StaticText(self, label="Please select an image to process", pos=(20, 65))

		# Button For selecting a Video File
		button =wx.Button(self, label="Choose Image...", pos=(20, 90))
		button.Bind(wx.EVT_BUTTON, self.onSelectFile)

		# Button for Going to the next panel -- Disabled until a video file has been chosen
		self.button1 =wx.Button(self, label="Paint", pos=(150, 90))
		self.button1.Bind(wx.EVT_BUTTON, self.paint)
		self.button1.Disable()

		# Variable for central image
		self.main_image = ''

		# Place Image of CARP logo
		png = wx.Image('./painter_gui/carp.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		wx.StaticBitmap(self, -1, png, (790, 20), (50,50))

		################### Decomposition Section ################### 
		txt3 = wx.StaticText(self, label="Decomposition", pos=(650, 130))
		self.num_colors = "0"
		self.decomp_num_colors = wx.TextCtrl(self, value=self.num_colors, pos=(650, 150))

		self.decomp_button_apply = wx.Button(self, label="Apply", pos=(650, 180))
		self.decomp_button_apply.Bind(wx.EVT_BUTTON, self.decomp)

		self.disable_decomp()

		####################  Recomposition Section ################### 
		txt4 = wx.StaticText(self, label="Recomposition", pos=(650, 230))
		txt5 = wx.StaticText(self, label="Select a Recomposition Method", pos=(650, 250))

		self.rb1 = wx.RadioButton(self, 11, label = 'Iterative Erosion', pos = (650, 280), style = wx.RB_GROUP) 
		self.rb2 = wx.RadioButton(self, 22, label = 'Skeleton',pos = (650, 300)) 
		self.rb3 = wx.RadioButton(self, 33, label = 'Blended Recomposition',pos = (650, 320))

		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb1.GetId())
		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb2.GetId())
		self.Bind(wx.EVT_RADIOBUTTON, self.SetVal, id=self.rb3.GetId())

		self.recomp_button_apply = wx.Button(self, label="Apply", pos=(700, 350))
		self.recomp_button_apply.Bind(wx.EVT_BUTTON, self.recomp)
		
		self.disable_recomp()

	def disable_decomp(self):
		self.decomp_num_colors.Disable()
		self.decomp_button_apply.Disable()

	def enable_decomp(self):
		self.decomp_num_colors.Enable()
		self.decomp_button_apply.Enable()

	def disable_recomp(self):
		self.rb1.Disable()
		self.rb2.Disable()
		self.rb3.Disable()
		self.recomp_button_apply.Disable()

	def enable_recomp(self):
		self.rb1.Enable()
		self.rb2.Enable()
		self.rb3.Enable()
		self.recomp_button_apply.Enable()

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

	# Method for performing decomp
	def decomp(self,event):
		print "Decomp"

	# Method for performing recomp
	def recomp(self,event):
		print "Recomp"

	def scale_bitmap(self, bitmap, width, height):
	    image = wx.ImageFromBitmap(bitmap)
	    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
	    result = wx.BitmapFromImage(image)
	    return result

    # Method for launching file dialog box
	def onSelectFile(self, event):
		global filename
		global dirname

        # Launch Dialog Box
		dlg = wx.FileDialog(self, "Choose a file", user.home, "","*.*")
		if dlg.ShowModal() == wx.ID_OK:
			# Save selected file name and directory
		    dirname = dlg.GetDirectory()
		    filename = dlg.GetFilename()

		    # Display Image
		    input_image = cv2.imread(dirname+"/"+filename)
		    
		    ideal = np.zeros([300, 300, 3])
		    ideal[:,:,0] = np.ones([300,300])*255
		    ideal[:,:,1] = np.ones([300,300])*255
		    ideal[:,:,2] = np.ones([300,300])*255

		    resized_image = resize_with_buffer(input_image , ideal)

		    cv2.imwrite('./painter_gui/resized.png', resized_image)

		    self.main_image = wx.Image('./painter_gui/resized.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		    wx.StaticBitmap(self, -1, self.main_image, (20, 130), (100,100))

		    # Report file selected and enable decomp section
		    self.txt2.SetLabel("Selected file: " + filename)
		    self.enable_decomp()

		# On Completion destroy dialog box
		dlg.Destroy()