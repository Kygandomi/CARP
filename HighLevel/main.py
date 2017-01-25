from recomposition.skeleton.skeletonRecompose import *
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.erosion.erosionRecompose import *
from common.util import *
import cv2

fname = 'resources/images/input/hands.png'

desiredImg = cv2.imread(fname, cv2.IMREAD_UNCHANGED)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)
(thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# recomposer = skeletonRecomposer(binImg, [2])
recomposer = iterativeErosionRecomposer(binImg, [10])
# recomposer = erosionRecomposer(binImg, [2])

LLT = recomposer.recompose()

testLLT(LLT,3)

print "Done"