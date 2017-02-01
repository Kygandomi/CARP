#!/usr/bin/env
import numpy as np
import cv2
import glob


# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# count !
count = 0;
cap = cv2.VideoCapture(1)
print ""

# Figure out where the camera is
# for i in range (1,1501):
#     cap = cv2.VideoCapture(1)
#     if (cap.open(1)):
#         print "Found camera " + str(i)
#         # break

while(True and count < 10):
    # Capture frame-by-frame
    ret1, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray,(0,0), fx=0.2, fy=0.2) 

    # Find the chess board corners
    ret2, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # If found, add object points, image points (after refining them)
    if ret2 == True:
        print "RET TRUE!"
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(gray, (7,6), corners2,ret2)
        cv2.imshow('img',img)
        cv2.waitKey(500)
        count += 1

    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print "***** RESULTS ******"
print mtx
print dist
print " "
print ret
print rvecs
print tvecs

cv2.destroyAllWindows()