import numpy as np
import cv2
import common.util as util

class iterativeErosionRecomposer(object):
    def __init__(self, image, args = []):

        self.desiredImage = image
        self.brush_thickness = args[0]

    def recompose(self):
        # desiredImg_grey = cv2.cvtColor(self.desiredImage, cv2.COLOR_BGR2GRAY)
        # (thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # util.display(binImg)

        binImg = self.desiredImage

        orders = []

        while self.hasColor(binImg,0):
            # util.display(binImg)
            binImg = cv2.dilate(binImg, util.circleKernel(3), iterations = self.brush_thickness)
            # util.display(binImg)

            contourImg, contours, hierarchy = cv2.findContours(255-binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
            # util.display(contourImg)

            for cnt_i in range(len(contours)):
                cnt = contours[cnt_i]
                stroke=[]
                for pt_i in range(0,len(cnt),10):
                    pt=cnt[pt_i][0]
                    # pt=util.mapToCanvas(pt,self.desiredImage.shape[:2])
                    stroke.append([pt[1] , pt[0], self.brush_thickness])
                stroke.append(stroke[0])
                orders.append(stroke)
        # drawnImg = util.draw(out_pts,np.array(255*np.ones((int(paper_size[0]),int(paper_size[1]))),dtype='uint8'),2)
        # util.display(drawnImg)

        return orders

    # TODO: use numpy to speed up?
    def hasColor(self, img, color):
        x = 0
        while x < img.shape[0]:
            y = 0
            while y < img.shape[1]:
                if img[x][y] == (color):
                    return True
                y += 1
            x += 1
        return False
