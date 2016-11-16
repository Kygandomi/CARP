import sys
import cv2
import numpy as np
import time

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

def order_points(pts):
  # initialzie a list of coordinates that will be ordered
  # such that the first entry in the list is the top-left,
  # the second entry is the top-right, the third is the
  # bottom-right, and the fourth is the bottom-left
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

debug = False # Set this to true if you want to see more images as the process happens.


cam = cv2.VideoCapture(1)   # value -> index of camera. My webcam was 0, USB camera was 1.
s, img = cam.read()

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

adaptiveThresholdedGray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

mask = np.zeros(adaptiveThresholdedGray.shape,np.uint8) # mask image the final image without small pieces

image, contours, other = cv2.findContours(adaptiveThresholdedGray,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE) # Gather the contours

long_contours = [] # Create an array for the long edges to be held

for cnt in contours:
    if 500<cv2.contourArea(cnt) < 850000: # Tuned to prevent small contours, but also not consider image edges a contour
        long_contours.append(cnt) # Record any long contours
        cv2.drawContours(img,[cnt],0,(0,255,0),2) # Draw those contours onto the image

rect = cv2.minAreaRect(long_contours[0]) # Generate a rectangle based on the long contour surrounding the page
box = cv2.boxPoints(rect) # Generate a box-point object from the rectangle

box = order_points(box) # Order the points so they were in proper order for transforms 

box = np.int0(box) # maths
cv2.drawContours(img,[box],0,(0,0,255),2) # Draw the actual contours so we can see them

if debug:
  cv2.imshow("test", img) 
  cv2.waitKey(0)
  cv2.destroyAllWindows()


if debug:
  canvas_image = four_point_transform(img, box) # Create the canvas image 
  cv2.imshow("test", canvas_image) 
  cv2.waitKey(0)
  cv2.destroyAllWindows()

while(True):
    s, img = cam.read() # Read the image again
    if s:    # frame captured without any errors
        canvas_image = four_point_transform(img, box) # Generate the canvas image based on the box's transform
        cv2.imshow("cam-test",canvas_image)
        cv2.waitKey(0)
        cv2.destroyWindow("cam-test")
        cv2.imwrite("imlog/capture" + str(int(time.time())) + ".jpg",canvas_image) #save image
