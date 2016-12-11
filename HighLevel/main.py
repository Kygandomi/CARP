from recomposition.skeleton.skeletonRecompose import *
from common.util import *
import cv2

fname = 'resources/images/input/pig.png'

desiredImg = cv2.imread(fname, cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)

recomposer = skeletonRecomposer(desiredImg_grey, [])
LLT = recomposer.recompose()

testLLT(LLT,3)

print "Done"