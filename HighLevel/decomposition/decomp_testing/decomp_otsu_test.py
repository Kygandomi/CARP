import cv2
from common import util

skull = util.getFileByName("dog2.png")
skull_2 = util.getFileByName_8UC1("dog2.png")

skull = cv2.cvtColor(skull, cv2.COLOR_BGR2GRAY)

util.display(skull, "Skull, unedited")

ret,th1 = cv2.threshold(skull,127,255,cv2.THRESH_BINARY)
util.display(th1, "binthresh")

ret,th2 = cv2.threshold(skull,127,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
util.display(th2, "adaptive thresh, mean")

ret,th3 = cv2.threshold(skull_2,0,255,cv2.THRESH_OTSU)
util.display(th3, "otsu")

skull_2 = cv2.GaussianBlur(skull_2,(9,9),0)
util.display(skull_2, "blurred skull_2")

ret,th4 = cv2.threshold(skull_2,0,255,cv2.THRESH_OTSU)
util.display(th4, "otsu with blurring first")

big_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
iterat = 2
opening = cv2.morphologyEx(th4, cv2.MORPH_OPEN, big_kernel, iterations=iterat)
closing = cv2.morphologyEx(th4, cv2.MORPH_CLOSE, big_kernel, iterations=iterat)
opening_the_close = cv2.morphologyEx(closing, cv2.MORPH_OPEN, big_kernel, iterations=iterat)

util.display(opening, "Opening")
util.display(closing, "closing")
util.display(opening_the_close, "close then open")



