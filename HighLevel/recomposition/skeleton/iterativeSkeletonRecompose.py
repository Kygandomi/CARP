import numpy as np
import cv2
import common.util as util
from recomposition.skeleton.medialAxisRecompose import *

class iterativeSkeletonRecomposer(object):
    def __init__(self, image, args = []):
        self.brush_thickness = args[0]
        self.desiredImage = util.open_image(image,3,self.brush_thickness)

    def recompose(self):
        LLT = []

        current_img = self.desiredImage.copy()
        # display(current_img)
        while self.hasColor(current_img,0):
            recomposer = medialAxisRecomposer(current_img, [self.brush_thickness])
            skel_LLT = recomposer.recompose()

            if(skel_LLT==[]):
                break

            current_img = drawLLT(skel_LLT,current_img,self.brush_thickness*3,255)
            current_img = util.open_image(current_img,3,self.brush_thickness)
            
            # display(testLLT(skel_LLT,scale=1,paper_size=current_img.shape),"skel llt")
            # display(current_img)

            LLT.extend(skel_LLT)
        
        return LLT

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