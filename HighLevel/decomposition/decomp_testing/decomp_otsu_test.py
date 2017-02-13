import sys
sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
sys.path.append('..\..\..\HighLevel')

import cv2
import random
from common import util
import numpy as np

#skull = #cv2.imread('../../resources/images/input/skull.jpg', cv2.IMREAD_UNCHANGED)
skull = util.getFileByName("dog2.png")
skull_2 = util.getFileByName_8UC1("dog2.png")

skull = cv2.cvtColor(skull, cv2.COLOR_BGR2GRAY)
#skull = 255-skull
#skull_2 = 255-skull_2

util.display(skull, "Skull, unedited")



#cv2.cvtColor(skull_2, cv2.COLOR_BGR2GRAY)

ret,th1 = cv2.threshold(skull,127,255,cv2.THRESH_BINARY)
util.display(th1, "binthresh")

ret,th2 = cv2.threshold(skull,127,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
util.display(th2, "adaptive thresh, mean")

#th3 = cv2.adaptiveThreshold(skull,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
#util.display(th3, "adaptive thresh, gaussian: SPOOKYMODE")


ret,th3 = cv2.threshold(skull_2,0,255,cv2.THRESH_OTSU)
util.display(th3, "otsu")
# util.save(th3, "1 otsu thresh")


skull_2 = cv2.GaussianBlur(skull_2,(9,9),0)
util.display(skull_2, "blurred skull_2")
# util.save(skull_2, "2 blurred skull")


ret,th4 = cv2.threshold(skull_2,0,255,cv2.THRESH_OTSU)
util.display(th4, "otsu with blurring first")
# util.save(th4, "3 otsu with blurring first")

# big_kernel = (5,5)

# big_kernel = np.ones((5,5),np.uint8)
big_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
iterat = 2
opening = cv2.morphologyEx(th4, cv2.MORPH_OPEN, big_kernel, iterations=iterat)
closing = cv2.morphologyEx(th4, cv2.MORPH_CLOSE, big_kernel, iterations=iterat)
opening_the_close = cv2.morphologyEx(closing, cv2.MORPH_OPEN, big_kernel, iterations=iterat)

util.display(opening, "Opening")
util.display(closing, "closing")
util.display(opening_the_close, "close then open")

# util.save(opening, "4 openning")
# util.save(closing, "5 closing")
# util.save(opening_the_close, "6 closing + openning")



