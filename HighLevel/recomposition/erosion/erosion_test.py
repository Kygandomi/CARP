import sys
sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
import cv2
from erosionRecompose import erosionRecomposer

desiredImg = cv2.imread('../../resources/images/input/cube.png', cv2.IMREAD_UNCHANGED)

recomposer = erosionRecomposer(desiredImg, [1])
print recomposer.recompose()

