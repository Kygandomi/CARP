from common.util import *
import sys
import graph
import cv2
import math
from skimage.morphology import medial_axis

def visualPolyDist(rawPolyImg):
    mini,maxi = np.abs(cv2.minMaxLoc(rawPolyImg)[:2])          # Find minimum and maximum to adjust colors
    #print "Min: "+str(mini)+" | Max: "+str(maxi)
    mini = 255.0/mini
    maxi = 255.0/maxi

    visualPolyImg = cv2.cvtColor(np.array(-1*np.ones(rawPolyImg.shape),dtype='uint8'),cv2.COLOR_GRAY2RGB)

    for i in xrange(rawPolyImg.shape[0]):                              
        for j in xrange(rawPolyImg.shape[1]):
            if rawPolyImg.item((i,j))<0:
                visualPolyImg.itemset((i,j,0),255-int(abs(rawPolyImg.item(i,j))*mini))   # If outside, blue color
                visualPolyImg.itemset((i,j,1),0)
                visualPolyImg.itemset((i,j,2),0)
            elif rawPolyImg.item((i,j))>0:
                visualPolyImg.itemset((i,j,0),0)
                visualPolyImg.itemset((i,j,1),0)#+int(rawPolyImg.item(i,j)*maxi))
                visualPolyImg.itemset((i,j,2),255-int(rawPolyImg.item(i,j)*maxi))        # If inside, red color
            else:
                visualPolyImg.itemset((i,j,0),255)
                visualPolyImg.itemset((i,j,1),255)
                visualPolyImg.itemset((i,j,2),255)                            # If on the contour, white color.
    return visualPolyImg

def pathFilter(path,sigma = 0):
    # mini,maxi = cv2.minMaxLoc(path)[:2]
    # nonzero = path[path > 0]
    # mid = np.median(nonzero)
    # sigma = .5
    # print mini, ", ",maxi
    # (thresh, pathImg) = cv2.threshold(path,sigma*maxi+(1-sigma)*mid, 255, cv2.THRESH_BINARY_INV)
    # pathImg = cv2.adaptiveThreshold(path,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,1)
    (thresh, pathImg) = cv2.threshold(path,127, 255, cv2.THRESH_OTSU)
    (thresh, pathImg) = cv2.threshold(path,thresh+int((255-thresh)*sigma), 255, cv2.THRESH_BINARY)
    return pathImg

class medialAxisRecomposer(object):

    def __init__(self, image, args):
        # opened = open_image(image,5,1);
        # self.binImg = cv2.erode(image,circleKernel(1),iterations=2)
        self.binImg = image

    def recompose(self):
        if np.count_nonzero(255-self.binImg)==0:
            return []

        binImg = cv2.erode(self.binImg,circleKernel(1),iterations=1)

        # (thresh, binImg) = cv2.threshold(self.desiredImage, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # display(self.binImg)

        skel, polyImg = medial_axis((255-binImg)/255.0, return_distance=True)

        # print distance
        # display(visualPolyDist(rawPolyImg))

        # mini,maxi = np.abs(cv2.minMaxLoc(distance)[:2])
        # polyImg = 1.0-distance/maxi
        # polyImg = scaledPolyDist(distance)
        # display(polyImg)

        ## Sobel/Scharr
        sobelx = cv2.Sobel(polyImg,cv2.CV_64F,1,0,ksize=-1)
        sobely = cv2.Sobel(polyImg,cv2.CV_64F,0,1,ksize=-1)
        sobel = sobelx*sobelx+sobely*sobely

        if np.count_nonzero(sobel)==0:
            return []

        # Convert to int scale. 0-255
        mini,maxi = cv2.minMaxLoc(sobel)[:2]
        sobel = (sobel * (255/maxi)).astype('uint8')
        sobel[np.where(cv2.dilate(binImg,circleKernel(1),iterations=2)==255)]=255

        # display(sobel)

        pathImg = pathFilter(sobel)

        # pathImg = self.skeletonize(self.binImg)
        ## Remove points that do not have enough neighbors
        # pathImg = self.neighborFilter(pathImg,3,-1,2,3)
        #display(pathImg)

        # display(overlay(self.binImg,pathImg,200),"skeleton")

        g = graph.graph(getPoints(pathImg,0),pathImg)
        paths = graph.findPaths(g)

        # output(graph.createNodeImg(pathImg,g),"nodes","images/output/")

        paths = reduceLLT(paths,2.9)
        paths = self.addWidth(paths,polyImg)

        # paths = mapLLT(paths,self.binImg.shape)

        return paths

    ################################################################
    ############# Helpers ##########################################
    ################################################################

    def addWidth(self,LLT,rawPolyImg):
        out_pts = []
        for path_i in range(len(LLT)):
            path = LLT[path_i]
            list_pts=[]
            for pt_i in range(len(path)):
                value = int(rawPolyImg.item(path[pt_i][0],path[pt_i][1]))
                pt=(path[pt_i][0],path[pt_i][1],value)
                list_pts.append(pt)
            out_pts.append(list_pts)
        return out_pts

    def neighborFilter(self,img,radius=3,border=-1,n_limit=1,iterations=1):
        neighbors = getNeighborPoints([0,0],circleKernel(radius,border))
        for i in range(iterations):
            pts = getPoints(img,255)
            for point in pts:
                if (point[0]>(radius+1)) and (point[1] > (radius+1)) and (img.shape[0]-point[0]>(radius+1)) and (img.shape[1]-point[1]>(radius+1)):
                    if np.count_nonzero(img[neighbors[:,0]+point[0],neighbors[:,1]+point[1]]) <= n_limit:
                        img[point]=0
        return img
