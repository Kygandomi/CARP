import numpy as np
import cv2
import common.util as util

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *

class blendedRecomposer(object):
    def __init__(self, image, args = []):
        self.brush_thickness = args[0]
        self.desiredImage = util.open_image(image,kernel_radius=self.brush_thickness)

    def recompose(self):
        skel_img = self.desiredImage.copy()
        erode_img = self.desiredImage.copy()
        erode_img = cv2.dilate(erode_img, util.circleKernel(3), iterations = self.brush_thickness*2)
        skel_img = 255-cv2.bitwise_xor(skel_img,erode_img)

        recomposer = skeletonRecomposer(skel_img, [self.brush_thickness])
        print "Running skeleton"
        skel_LLT = recomposer.recompose()
        recomposer = iterativeErosionRecomposer(self.desiredImage, [self.brush_thickness])
        print "Running iterative erosion"
        erode_LLT = recomposer.recompose()

        LLT = []
        LLT.extend(erode_LLT)
        LLT.extend(skel_LLT)
        return LLT
