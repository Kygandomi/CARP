import cv2
import common.util as util

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.medialAxisRecompose import *

class blendedRecomposer(object):
    """
    This recomposer uses the iterative erostion and medial axis recomposers.

    The image to be eroded is first dillated, while the copy of the image for medial axis recomp
    is inverted.

    These images are then processed using the related recomposers and then an LLT is generated
    that takes inputs from both.
    """
    def __init__(self, image, args = []):
        self.brush_thickness = args[0]
        self.desiredImage = util.open_image(image,kernel_radius=self.brush_thickness)

    def recompose(self):
        skel_img = self.desiredImage.copy()
        erode_img = self.desiredImage.copy()
        erode_img = cv2.dilate(erode_img, util.circleKernel(3), iterations = int(self.brush_thickness))
        skel_img = 255-cv2.bitwise_xor(skel_img,erode_img)

        # display(self.desiredImage,"original")
        # display(erode_img,"eroded")
        # display(skel_img,"skeleton")

        recomposer = medialAxisRecomposer(skel_img, [self.brush_thickness])
        skel_LLT = recomposer.recompose()
        recomposer = iterativeErosionRecomposer(self.desiredImage, [self.brush_thickness])
        erode_LLT = recomposer.recompose()

        # display(testLLT(skel_LLT,scale=1,paper_size=skel_img.shape),"skel llt")
        # display(testLLT(erode_LLT,scale=1,paper_size = erode_img.shape),"erode llt")

        LLT = []
        LLT.extend(erode_LLT)
        LLT.extend(skel_LLT)
        return LLT
