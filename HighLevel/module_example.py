# This file is here as an example of how to import things from modules that we make.
# If anything is unclear then ask Odell

# from camera (a user-made module) we import * (all modules imported in camera/__init__.py)
from camera import *
import cv2

# Instantiate a Camera object form the CanvasCamera module within the camera module
cam = CanvasCamera.Camera(1)

# Write the canvas image to a file.
cv2.imwrite("test.png", cam.get_canvas())