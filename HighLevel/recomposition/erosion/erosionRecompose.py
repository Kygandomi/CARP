import numpy as np
import cv2
from common.util import *


class erosionRecomposer(object):

    def __init__(self, image, args):
        """

        :param image: The source image to recompose
        :param args: [brush_thickness]
        :return:
        """
        self.desiredImage = image
        self.brush_thickness = args[0]

    def recompose(self):

        paper_size = (11*25.4,8.5*25.4)

        desiredImg_grey = cv2.cvtColor(self.desiredImage, cv2.COLOR_BGR2GRAY)

        (thresh, binImg) = cv2.threshold(desiredImg_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # util.display(binImg)
        binImg = cv2.dilate(binImg, util.circleKernel(1), iterations = self.brush_thickness)
        # util.display(binImg)

        contourImg, contours, hierarchy = cv2.findContours(255-binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
        # util.display(contourImg)
        orders = []

        n_points = 0
        out_pts = []
        for cnt_i in range(len(contours)):
            cnt = contours[cnt_i]
            list_pts=[]
            for pt_i in range(0,len(cnt),10):
                pt=cnt[pt_i][0]

                pt=util.mapToCanvas(pt,self.desiredImage.shape[:2],paper_size)

                orders.append([pt[0] , pt[1], self.brush_thickness])

                list_pts.append(pt)

                n_points += 1
            out_pts.append(list_pts)

        drawnImg = util.draw(out_pts,np.array(255*np.ones((int(paper_size[0]),int(paper_size[1]))),dtype='uint8'),2)
        util.save(drawnImg)
        return orders