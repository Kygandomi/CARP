import pointillismRecompose as rc
import cv2

import os; print(os.getcwd())

desiredImg = cv2.imread('../../resources/images/input/box.png', cv2.IMREAD_UNCHANGED)

recomposer = rc.pointillismRecomposer(desiredImg, [25, 50, 50])
print recomposer.recompose()
