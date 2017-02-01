#!/usr/bin/env
import numpy as np
import cv2

mtx = np.array([[  377.78673528,    0,          288.69241399 ],
				[   0,          371.34756677,  170.72855335],
				[   0,            0,            1        ]])


dist = np.array([-0.37584068,  0.13246873,  0.00213057, -0.00719296, -0.01824359])


# Figure out where the camera is
for i in range (2,1501):
	cap = cv2.VideoCapture(1)
	if (cap.open(1)):
	    print "Found camera " + str(1)
	    break

# Once we have the camera, stream video
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(frame,(0,0), fx=0.2, fy=0.2)  
    h,  w = gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    dst = cv2.undistort(gray, mtx, dist, None, newcameramtx)

    # mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
    # dst = cv2.remap(gray,mapx,mapy,cv2.INTER_LINEAR)

    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]

    # Display the resulting frame
    print "shape ", dst.shape
    # cv2.imshow('frame',dst)
    cv2.imshow('orig', dst)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

