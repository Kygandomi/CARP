import sys

sys.path.append('/usr/local/lib/python2.7/site-packages') # This makes it work on Odell's computer

import cv2
import random
from HighLevel.common import util


class pointillismRecomposer(object):


    def __init__(self, image, args):
        """
        :param image: The image that is being recomposed
        :param args: [width of brush], here we take in an array containing 1 element, the width of the brush dot in px.
        :return:
        """
        self.width = args[0]
        self.strokesToMake = args[1]
        self.childrenPerGeneration = args[2]

        self.desiredImage = image

        self.strokeImg = cv2.imread('smallstroke.png', cv2.IMREAD_UNCHANGED)
        self.strokeImg = cv2.resize(self.strokeImg, (self.width, self.width))

        print self.width
        print self.strokeImg.shape

        r, w, ch = self.desiredImage.shape

        self.canvasImg = cv2.imread('../../resources/images/input/canvas.png', cv2.IMREAD_UNCHANGED)
        cv2.resize(self.canvasImg, (r,w))

    def makeStroke(self, canvas, stroke, pos):
        """Places nontransperant pixels from the stroke image into the canvas image.
        pos is the position on the CANVAS where the (0,0) pixel from the STROKE will be placed."""
        offsetx, offsety = pos # Depackage the x and y positions
        stroke_rows, stroke_cols, stroke_channels = stroke.shape # Get the strome image info
        for x in range(0, stroke_cols): # For each column in the stroke
            for y in range (0, stroke_rows): # For each row in the stroke
                if (stroke[x, y])[3] > 120: # If it is a nontransperant pixel
                    canvas[offsetx + x, offsety + y] = stroke[x, y] # Attempt to paint that pixel to the canvas
        return canvas

    def fastNorm(self,img1, img2):
        resized_img1 = cv2.resize(img1, (100, 100))
        resized_img2 = cv2.resize(img2, (100, 100))
        return cv2.norm(resized_img1, resized_img2, cv2.NORM_L1)

    def recompose(self):
        canvas_rows, canvas_cols, canvas_channels = self.canvasImg.shape
        stroke_rows, stroke_cols, stroke_channels = self.strokeImg.shape

        strokes = 0

        currentBestCanvas = self.canvasImg.copy()

        orders = []

        while strokes < self.strokesToMake:
            possible_canvases = []
            strokeCoordinates = []

            bestError = 9999999999 # @TODO: Make this not stupid
            numBestError = 0

            for i in range(0, self.childrenPerGeneration):
                canvas = currentBestCanvas.copy()
                possible_canvases.append(canvas)

            i = 0
            for canvas_to_paint_randomly in possible_canvases:
                limit_x = canvas_cols - stroke_cols
                limit_y = canvas_rows - stroke_rows
                x = random.randint(0,limit_x)
                y = random.randint(0,limit_y)
                self.makeStroke(canvas_to_paint_randomly, self.strokeImg, (x, y))
                strokeCoordinates.append((((y*1.0)*(8.5*25.4/1000)), ((x*1.0)*(11*25.4/1000)), self.width ))
                i+=1

            for i in range(0, self.childrenPerGeneration):
                mse = self.fastNorm(possible_canvases[i], self.desiredImage)
                if mse < bestError:
                    bestError = mse
                    numBestError = i
            print "Best one was number ", numBestError
            currentBestCanvas = possible_canvases[numBestError]
            print strokeCoordinates[numBestError]
            orders.append([strokeCoordinates[numBestError], strokeCoordinates[numBestError]])
            print "Strokes left: ", self.strokesToMake - strokes -1
            strokes += 1

        util.save(currentBestCanvas)
        return orders

