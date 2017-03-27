import cv2
import common.util as util

class iterativeErosionRecomposer(object):
    def __init__(self, image, args = []):

        self.desiredImage = image
        self.brush_thickness = args[0]


    def hasColor(self, img, color):
        x = 0
        while x < img.shape[0]:
            y = 0
            while y < img.shape[1]:
                if img[x][y] == color:
                    return True
                y += 1
            x += 1
        return False

    def recompose(self):

        binImg = self.desiredImage

        orders = []

        while self.hasColor(binImg,0):

            # Dillate the white in the image, causing the drawn sections of the image to be eroded.
            binImg = cv2.dilate(binImg, util.circleKernel(3), iterations = self.brush_thickness)

            contourImg, contours, hierarchy = cv2.findContours(255-binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)

            # Build a set of instructions based on the contour determined by the dillation.
            for cnt_i in range(len(contours)):
                cnt = contours[cnt_i]
                stroke=[]
                for pt_i in range(0,len(cnt),10):
                    pt=cnt[pt_i][0]
                    stroke.append([pt[1] , pt[0], self.brush_thickness])
                stroke.append(stroke[0])
                orders.append(stroke)

        return orders

