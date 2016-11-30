import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import cv2
import random
import numpy as np

from HighLevel.recomposition.abstractRecompose import absRecompose as rc

class pointalismRecomposer(rc.recomposer):


    def __init__(self, image, args):
        """
        :param image:
        :param args:
        :return:
        """
        rc.recomposer.__init__(self, image, args)

        self.desiredImage = image
        width = args[0]
        #self.strokeImg = cv2.resize(cv2.imread('smallstroke.png', cv2.IMREAD_UNCHANGED), (width, width))
        self.strokeImg = cv2.imread('smallstroke.png', cv2.IMREAD_UNCHANGED)
        self.display(self.strokeImg, "stroke")
        r, w, ch = self.desiredImage.shape
        self.canvasImg = cv2.resize(cv2.imread('canvas.png', cv2.IMREAD_UNCHANGED), (r,w))
        self.display(self.canvasImg, "canvas")


    def display(self, img, name):
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def makeStroke(self, canvas, stroke, pos):
        """Places nontransperant pixels from the stroke image into the canvas image.
        pos is the position on the CANVAS where the (0,0) pixel from the STROKE will be placed."""
        offsetx, offsety = pos # Depackage the x and y positions
        canvas_rows, canvas_cols, canvas_channels = canvas.shape # Get the canvas image info
        stroke_rows, stroke_cols, stroke_channels = stroke.shape # Get the strome image info
        for x in range(0, stroke_cols): # For each column in the stroke
            for y in range (0, stroke_rows): # For each row in the stroke
                if ((stroke[x, y])[3] > 120): # If it is a nontransperant pixel
                    canvas[offsetx + x, offsety + y] = stroke[x, y] # Attempt to paint that pixel to the canvas
        return canvas

    def calcMSE(self,img1, img2):
        """lol this doesn't do an MSE it just uses cv2's norm"""
        sum = 0.0
        resized_img1 = cv2.resize(img1, (100, 100))
        resized_img2 = cv2.resize(img2, (100, 100))
        return cv2.norm(resized_img1, resized_img2, cv2.NORM_L1)

    def recompose(self):
        canvas_rows, canvas_cols, canvas_channels = self.canvasImg.shape
        stroke_rows, stroke_cols, stroke_channels = self.strokeImg.shape

        strokes = 0
        strokesToMake = 50

        childrenPerGeneration = 50

        currentBestCanvas = self.canvasImg.copy()

        orders = open("orders.txt", 'w')

        while strokes < strokesToMake:
            possible_canvases = []
            strokeCoordinates = []

            bestError = 9999999999 # @TODO: Make this not stupid
            numBestError = 0

            for i in range(0, childrenPerGeneration):
                canvas = currentBestCanvas.copy()
                possible_canvases.append(canvas)

            i = 0
            for canvas_to_paint_randomly in possible_canvases:
                limit_x = canvas_cols - stroke_cols
                limit_y = canvas_rows - stroke_rows
                x = random.randint(0,limit_x)
                y = random.randint(0,limit_y)
                canvas_to_paint_randomly = self.makeStroke(canvas_to_paint_randomly, self.strokeImg, (x, y))
                strokeCoordinates.append(str((y*1.0)*(8.5*25.4/1000)) + " " + str((x*1.0)*(11*25.4/1000)))
                i+=1

            for i in range(0, childrenPerGeneration):
                mse = self.calcMSE(possible_canvases[i], self.desiredImage)
                if mse < bestError:
                    bestError = mse
                    numBestError = i
            print "Best one was number ", numBestError
            currentBestCanvas = possible_canvases[numBestError]
            print strokeCoordinates[numBestError]
            orders.write(strokeCoordinates[numBestError] + '\n')
            print "Strokes left: ", strokesToMake - strokes -1


            strokes += 1
        self.display(currentBestCanvas, "Hey did it work?")

