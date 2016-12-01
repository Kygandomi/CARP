from recomposition.skeleton import skeletonRecompose
from common.util import *
import cv2

fname = 'resources/images/input/hands.png'

desiredImg = cv2.imread(fname, cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)

LLT = skeletonRecompose.recompose(desiredImg_grey,3)

testLLT(LLT,3)

print "Done"