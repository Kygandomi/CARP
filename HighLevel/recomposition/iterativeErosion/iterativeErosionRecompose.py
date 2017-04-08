import cv2
import common.util as util

class iterativeErosionRecomposer(object):
    def __init__(self, image, args = []):

        self.binImg = image
        self.brush_thickness = args[0]

    def recompose(self):

        binImg = self.binImg

        orders = []

        n_iter=1

        while 1:

            # Dillate the white in the image, causing the drawn sections of the image to be eroded.
            binImg = cv2.dilate(binImg, util.circleKernel(self.brush_thickness), iterations = n_iter)
            n_iter=2; # First erosion is by radius. Next are by diameter

            contourImg, contours, hierarchy = cv2.findContours(255-binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)

            if len(contours) == 0:
                return orders

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

