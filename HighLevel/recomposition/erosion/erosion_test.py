import cv2
from erosionRecompose import erosionRecomposer

desiredImg = cv2.imread('../../resources/images/input/cube.png', cv2.IMREAD_UNCHANGED)

recomposer = erosionRecomposer(desiredImg, [1])
print recomposer.recompose()

