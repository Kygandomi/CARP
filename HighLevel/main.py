from recomposition.skeleton.skeletonRecompose import *
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.erosion.erosionRecompose import *
from common.util import *
import cv2

desiredImg = readImage("dog2.png")

display(desiredImg)

desiredImg_grey = cv2.cvtColor(desiredImg, cv2.COLOR_BGR2GRAY)
(thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

display(binImg)

# recomposer = skeletonRecomposer(binImg, [2])
recomposer = iterativeErosionRecomposer(binImg, [2])
# recomposer = erosionRecomposer(binImg, [2])

LLT = recomposer.recompose()

testLLT(LLT,scale=3,thickness=6)

print "Done"