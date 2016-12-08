import sys
sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer
import cv2
from skeletonRecompose import skeletonRecomposer

desiredImg = cv2.imread('../../resources/images/input/pig.png', cv2.CV_8UC1)

recomposer = skeletonRecomposer(desiredImg, [])
print recomposer.recompose()

