#!/usr/bin/env
import numpy as np
import cv2
from common import util


mtx =np.array([[  1.10631110e+03,   0.00000000e+00,   6.76280470e+02],
 [  0.00000000e+00,   1.10214590e+03,   2.61620659e+02],
 [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
dist = np.array([[-0.47479333,  0.23125714,  0.01108992,  0.00123208, -0.04514544]])

cap = None

# Figure out where the camera is
for i in range (0,1501):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print "Found camera " + str(i)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        break
    else:
        cap.release()

# Once we have the camera, stream video
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    print frame.shape

    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = frame
    # gray = cv2.resize(frame,(0,0), fx=0.2, fy=0.2)
    h,  w = gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    util.display(gray)
    dst = cv2.undistort(gray, mtx, dist, None, newcameramtx)

    # mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
    # dst = cv2.remap(gray,mapx,mapy,cv2.INTER_LINEAR)

    x,y,w,h = roi

    dst = dst[y:y+h, x:x+w]
    util.display(dst)


    # Display the resulting frame
    print "shape ", dst.shape
    # cv2.imshow('frame',dst)
    print dst
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

