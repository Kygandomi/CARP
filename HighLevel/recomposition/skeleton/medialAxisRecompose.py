from common.util import *
import sys
import graph
import cv2
import math

def parents(hierarchy):
    # [Next, Prev, 1st Child, Parent]
    i=0
    h_out = []
    for count in range(len(hierarchy)):
        if(hierarchy[i][0] == -1):
            h_out.append(i)
            return h_out
        else:
            h_out.append(i)
            i=hierarchy[i][0]
    return h_out

def childrenOf(hierarchy, i):
    # [Next, Prev, 1st Child, Parent]
    h_out = []
    for count in range(len(hierarchy)):
        if(hierarchy[count][3] == i):
            h_out.append(count)
    return h_out

def ptsInContours(contours,hierarchy,shape):
    cntr_pts = []
    # For each list of contour points...
    for i in range(len(contours)):
        # Create a mask image that contains the contour filled in
        cimg = np.zeros(shape)
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)
        if(hierarchy[i][2]!=-1):
            cimg = cv2.erode(cimg, circleKernel(1))
            for child_i in childrenOf(hierarchy,i):
                cv2.drawContours(cimg, contours, child_i, color=0, thickness=-1)
            cimg = cv2.dilate(cimg, circleKernel(1))
        # Access the image pixels and create a 1D numpy array then add to list
        cntr_pts.append(getPoints(cimg))
    return cntr_pts

def rawPolyDist(binImg):
    contourImg, contours, hierarchy = cv2.findContours(binImg.copy(),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    hierarchy = hierarchy[0]

    rawPolyImg = np.array(-1.0*np.ones(binImg.shape),dtype='float32')

    cntr_pts = ptsInContours(contours,hierarchy,binImg.shape)
    i_parents = parents(hierarchy)
    count = 1
    max_count = len(i_parents)
    for cnt_i in i_parents:
        # print "Analyzing Contour "+str(count)+" of "+str(max_count)
        list_pts = cntr_pts[cnt_i]
        for pt in list_pts:
            value = cv2.pointPolygonTest(contours[cnt_i],(pt[1],pt[0]),True)
            if(hierarchy[cnt_i][2]!=-1):
                min_val2 = -value
                for child_i in childrenOf(hierarchy,cnt_i):
                    value2 = cv2.pointPolygonTest(contours[child_i],(pt[1],pt[0]),True)
                    min_val2 = max(min_val2,value2)
                value = min(value,-(min_val2))
            rawPolyImg.itemset(pt,value)
        count = count + 1
    # print "Contour Analysis Complete"
    return rawPolyImg, contours, hierarchy, cntr_pts

def scaledPolyDist(rawPolyImg):
    mini,maxi = np.abs(cv2.minMaxLoc(rawPolyImg)[:2])          # Find minimum and maximum to adjust colors
    #print "Min: "+str(mini)+" | Max: "+str(maxi)
    maxi = 1.0/maxi

    scaledPolyImg = np.array(-1*np.ones(rawPolyImg.shape),dtype='float32')

    for i in xrange(rawPolyImg.shape[0]):                              
        for j in xrange(rawPolyImg.shape[1]):
            if rawPolyImg.item((i,j))>0:
                scaledPolyImg.itemset((i,j),1.0-rawPolyImg.item(i,j)*maxi)        # If inside, gradient to dark
            else:
                scaledPolyImg.itemset((i,j),1.0)        # If outside, white

    return scaledPolyImg

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

def pathFilter(path):
    # mini,maxi = cv2.minMaxLoc(path)[:2]
    # nonzero = path[path > 0]
    # mid = np.median(nonzero)
    # sigma = .5
    # (thresh, pathImg) = cv2.threshold(path,sigma*maxi+(1-sigma)*mid, 255, cv2.THRESH_BINARY_INV)
    # pathImg = cv2.adaptiveThreshold(path,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,55,10)
    (thresh, pathImg) = cv2.threshold(path,127, 255, cv2.THRESH_OTSU)
    return pathImg

class medialAxisRecomposer(object):

    def __init__(self, image, args):
        self.binImg = cv2.erode(image,circleKernel(1),iterations=1)

    def recompose(self):

        # (thresh, binImg) = cv2.threshold(self.desiredImage, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # display(self.binImg)

        rawPolyImg,contours,hierarchy,cntr_pts = rawPolyDist(255-self.binImg)
        # display(visualPolyDist(rawPolyImg))
        polyImg = scaledPolyDist(rawPolyImg)
        # display(polyImg)

        ## Sobel/Scharr
        sobelx = cv2.Sobel(polyImg,cv2.CV_64F,1,0,ksize=-1)
        sobely = cv2.Sobel(polyImg,cv2.CV_64F,0,1,ksize=-1)
        sobel = sobelx*sobelx+sobely*sobely

        # Convert to int scale. 0-255
        mini,maxi = cv2.minMaxLoc(sobel)[:2]
        sobel = (sobel * (255/maxi)).astype('uint8')
        sobel[np.where(cv2.dilate(self.binImg,circleKernel(2),iterations=1)==255)]=255

        # display(sobel)

        pathImg = pathFilter(sobel)

        # pathImg = self.skeletonize(self.binImg)
        ## Remove points that do not have enough neighbors
        # pathImg = self.neighborFilter(pathImg,3,-1,2,3)
        #display(pathImg)

        g = graph.graph(getPoints(pathImg,0))
        paths = graph.findPaths(g)

        # display(self.createNodeImg(pathImg,g))

        paths = reduceLLT(paths,2.9)
        paths = self.addWidth(paths,rawPolyImg)

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

    def createNodeImg(self, pathImg, g):
        nodeImg = cv2.cvtColor(pathImg.copy(),cv2.COLOR_GRAY2BGR)
        for node in g.node_list:
            if node.status == graph.node.End:
                nodeImg[node.point[0],node.point[1]] = (0,0,255)
            elif node.status == graph.node.Path:
                nodeImg[node.point[0],node.point[1]] = (0,255,255)
            elif node.status == graph.node.Dead:
                nodeImg[node.point[0],node.point[1]] = (128,128,128)
            elif node.status == graph.node.Visited:
                nodeImg[node.point[0],node.point[1]] = (255,0,0)
        return nodeImg

