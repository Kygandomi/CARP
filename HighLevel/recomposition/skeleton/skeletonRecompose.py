from common.util import *
import graph
import cv2

def recompose(image,args):
    (thresh, binImg) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 

    pathImg = skeletonize(binImg)

    #display(self.createNodeImg(pathImg))

    ## Remove points that do not have enough neighbors

    radius = 3
    border = -1
    n_limit = 1
    neighbors = getNeighborPoints([0,0],circleKernal(radius,border))
    pts = getPoints(pathImg,255)
    for point in pts:
        if pathImg[point] != 0:
            if np.count_nonzero(pathImg[neighbors[:,0]+point[0],neighbors[:,1]+point[1]]) <= n_limit:
                pathImg[point]=0
    g = graph.graph(getPoints(pathImg,255))
    paths = graph.findPaths(g)

    paths = reducePaths(paths,1000)

    paths = mapLLT(paths,image.shape)

    return paths

################################################################
############# Helpers ##########################################
################################################################

def skeletonize(binImg):
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    #element = circleKernal(1)
    done = False

    img = 255-binImg.copy()
    skel = np.zeros(img.shape,np.uint8)

    while( not done):
        eroded = cv2.erode(img,element)
        temp = cv2.dilate(eroded,element)
        temp = cv2.subtract(img,temp)
        skel = cv2.bitwise_or(skel,temp)
        img = eroded.copy()

        nonzero = cv2.countNonZero(img)
        if nonzero==0:
            done = True

    return skel

def createNodeImg(pathImg):
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

def reducePaths(paths,desired_n_points):
    step = 1+int(sum(len(path) for path in paths)/desired_n_points)

    out_pts = []
    for path_i in range(len(paths)):
        path = paths[path_i]
        list_pts=[]
        for pt_i in range(0,len(path),step):
            pt=path[pt_i]
            #pt=(8.5*25.4/1000)*pt
            
            list_pts.append(pt)
        out_pts.append(list_pts)
    return out_pts

if __name__ == "__main__":
   recompose(sys.argv[1],sys.argv[2])