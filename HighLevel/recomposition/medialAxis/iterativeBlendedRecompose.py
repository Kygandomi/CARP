import cv2
import numpy as np
import common.util as util
import medialAxisRecompose

class iterativeBlendedRecomposer(object):
    """
    This recomposer uses the iterative erostion and medial axis recomposers.

    The image to be eroded is first dilated, while the copy of the image for medial axis recomp
    is inverted.

    These images are then processed using the related recomposers and then an LLT is generated
    that takes inputs from both.
    """
    def __init__(self, image,args = []):
        self.brush_thickness = args[0]
        if len(args)<2 or args[1] is None:
            self.recomp_thin = medialAxisRecompose.medialAxisRecomposer(image,args)
        else:
            self.recomp_thin = args[1]
        # self.binImg = util.open_image(image,kernel_radius=self.brush_thickness)
        self.binImg = image

    def recompose(self):
        if np.count_nonzero(255-self.binImg)==0:
            return []

        skel_img = self.binImg.copy()
        erode_img = self.binImg.copy()
        erode_img = cv2.dilate(erode_img, util.circleKernel(self.brush_thickness), iterations = 2)
        skel_img = 255-cv2.bitwise_xor(skel_img,erode_img)

        # display(self.desiredImage,"original")
        # util.display(erode_img,"eroded")
        # util.display(skel_img,"skeleton")

        self.recomp_thin.binImg = skel_img;
        skel_LLT = self.recomp_thin.recompose()
        # util.display(util.overlay(skel_img,util.testLLT(skel_LLT,scale=1,paper_size=skel_img.shape),200),"path")

        self.binImg = erode_img
        erode_LLT = self.recompose()
        

        LLT = []
        LLT.extend(erode_LLT)
        LLT.extend(skel_LLT)
        return LLT
