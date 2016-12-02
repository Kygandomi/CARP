import pointalismRecompose as rc
import cv2

desiredImg = cv2.imread('../../resources/images/input/cat.png', cv2.IMREAD_UNCHANGED)

recomposer = rc.pointalismRecomposer(desiredImg, [10])
recomposer.recompose()
