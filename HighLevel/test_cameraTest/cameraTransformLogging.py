import sys
import cv2
import numpy as np
import time

from CameraException import *

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer



def get_image(camera_value):
  cam = cv2.VideoCapture(camera_value)   # value -> index of camera. My webcam was 0, USB camera was 1.
  s, img = cam.read()
  if s:    # frame captured without any errors
      cv2.imwrite("camera_image.jpg",img) #save image
      return img
  else:
      raise CameraReadError("Unable to read from camera " + str(camera_value))

def order_points(pts):
  """Given an array of points defining a square, this will return them ordered 
  such that will be ordered such that the first entry in the list is the top-left, 
  the second entry is the top-right, the third is the bottom-right, and the fourth is the bottom-left. """

  rect = np.zeros((4, 2), dtype = "float32")
  # the top-left point will have the smallest sum, whereas
  # the bottom-right point will have the largest sum
  s = pts.sum(axis = 1)
  rect[0] = pts[np.argmin(s)]
  rect[2] = pts[np.argmax(s)]

  # now, compute the difference between the points, the
  # top-right point will have the smallest difference,
  # whereas the bottom-left will have the largest difference
  diff = np.diff(pts, axis = 1)
  rect[1] = pts[np.argmin(diff)]
  rect[3] = pts[np.argmax(diff)]

  # return the ordered coordinates
  return rect

def four_point_transform(image, pts):
  """ Given an image and pts where pts is an ordered set of rectangle-defining points,
  this will return the subset of the image defined by those points, warped dimensionally
  to fit into a square. This handles linear translation, angular orientation, and warping.
  """
  # obtain a consistent order of the points and unpack them
  # individually
  rect = order_points(pts)
  (tl, tr, br, bl) = rect

  # compute the width of the new image, which will be the
  # maximum distance between bottom-right and bottom-left
  # x-coordiates or the top-right and top-left x-coordinates
  widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
  widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
  maxWidth = max(int(widthA), int(widthB))

  # compute the height of the new image, which will be the
  # maximum distance between the top-right and bottom-right
  # y-coordinates or the top-left and bottom-left y-coordinates
  heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
  heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
  maxHeight = max(int(heightA), int(heightB))

  # now that we have the dimensions of the new image, construct
  # the set of destination points to obtain a "birds eye view",
  # (i.e. top-down view) of the image, again specifying points
  # in the top-left, top-right, bottom-right, and bottom-left
  # order
  dst = np.array([
    [0, 0],
    [maxWidth - 1, 0],
    [maxWidth - 1, maxHeight - 1],
    [0, maxHeight - 1]], dtype = "float32")

  # compute the perspective transform matrix and then apply it
  M = cv2.getPerspectiveTransform(rect, dst)
  warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

  # return the warped image
  return warped

def get_transform(image):
    gray_image = cv2.cvtColor(camera_image,cv2.COLOR_BGR2GRAY)

    adaptive_thresholded = cv2.adaptiveThreshold(gray_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    image, contours, other = cv2.findContours(adaptive_thresholded,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE) # Gather the contours

    long_contours = [] # Create an array for the long edges to be held

    for cnt in contours:
        if 15000<cv2.contourArea(cnt) < 850000: # Tuned to prevent small contours, but also not consider image edges a contour
            long_contours.append(cnt) # Record any long contours
            cv2.drawContours(image,[cnt],0,(0,255,0),2) # Draw those contours onto the image

    try:
        rect = cv2.minAreaRect(long_contours[0]) # Generate a rectangle based on the long contour surrounding the page
    except IndexError:
        raise CameraReadError("Unable to get contours from camera image, check that camera image isn't washed out.")
        return
    box = cv2.boxPoints(rect) # Generate a box-point object from the rectangle

    box = order_points(box) # Order the points so they were in proper order for transforms 

    box = np.int0(box) # maths

    return box

# This is for testing.
camera_image = get_image(1)

transform = get_transform(camera_image)

# This will write a transformed image out every 5 seconds.
while(True):
    try:
        img = get_image(1)
        canvas_image = four_point_transform(img, transform) # Generate the canvas image based on the box's transform
        cv2.imwrite("imlog/capture_" + str(int(time.time())) + ".jpg",canvas_image) #save image
        time.sleep(5)
    except CameraReadError as e:
        print e.args[0]
