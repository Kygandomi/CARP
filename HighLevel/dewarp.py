#!/usr/bin/env
import numpy as np
import cv2
from common import util


#PURE
# mtx = np.array([[  4.93988251e+03 ,  0.00000000e+00 ,  6.67427894e+02],
#  [  0.00000000e+00 ,  5.29553206e+03  , 4.49712265e+02],
#  [  0.00000000e+00 ,  0.00000000e+00 , 1.00000000e+00]])
# dist = np.array([[ -1.10157126e+01 ,  1.27727231e+02 , -1.25121362e-02  ,-4.19927722e-03,
#    -1.67823487e+02]])


#
# mtx = np.array([[  1.92027260e+03  , 0.00000000e+00  , 6.66962550e+02],
#  [  0.00000000e+00  , 2.03582551e+03 ,  4.83589076e+02],
#  [  0.00000000e+00 ,  0.00000000e+00 ,  1.00000000e+00]])
#
#
# dist = np.array([[ -1.74311294e+00  , 4.25385425e+00 , -2.27071372e-02 , -3.22666440e-03
#    -5.72778745e+00]])


# mtx = np.array([[  1.51776952e+03 ,  0.00000000e+00 ,  6.69301655e+02],
#  [  0.00000000e+00 ,  1.62220480e+03  , 4.56816996e+02],
#  [  0.00000000e+00 ,  0.00000000e+00  , 1.00000000e+00]])
#
#
# dist = np.array([[  -1.06519345e+00  , 1.48786155e+00 ,  1.50016038e-03 ,  1.15564971e-03,
#    -1.14478176e+00]])

# 1280x720 explicit
# mtx =np.array([[  3.27883097e+03,   0.00000000e+00,   6.96403696e+02],
#  [  0.00000000e+00,   3.24579827e+03,   3.58979742e+02],
#  [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])

# dist = np.array([[ -5.20198790e+00,   4.34976376e+01,  -9.40246662e-02,  -6.79239647e-02,
#    -9.97008945e+01]]) 

mtx =np.array([[  1.10631110e+03,   0.00000000e+00,   6.76280470e+02],
 [  0.00000000e+00,   1.10214590e+03,   2.61620659e+02],
 [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
dist = np.array([[-0.47479333,  0.23125714,  0.01108992,  0.00123208, -0.04514544]])

cap = None
# Figure out where the camera is
for i in range (0,1501):
    cap = cv2.VideoCapture(i)
    if (cap.isOpened()):
        print "Found camera " + str(i)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720);
        break
    else:
        cap.release()

# Once we have the camera, stream video
while(True):
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

