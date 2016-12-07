import numpy as np
import cv2

def display(img, name="img"):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save(img, name="test_image"):
    cv2.imwrite(name+".png", img)

def output(img,name="output"):
    save(img,name)
    display(img,name)

def circleKernel(radius,thickness = -1):
    """ Return a kernal representing a circle with the given radius and thickness (in pixels)"""
    brush = cv2.circle(np.zeros((radius*2+1,radius*2+1)),(radius,radius),radius,1,thickness).astype('uint8')
    return brush

def getPoints(img,color=255):
    """ Return a list of points in a grayscale image which are of the given value. Default 255 (black)"""
    pts = np.array(np.where(img == 255))
    # print pts
    real_pts = []
    for j in range(len(pts[0])):
        real_pts.append((pts[0][j],pts[1][j]))
    # print real_pts
    return real_pts

def getNeighborPoints(pt,kernel = np.ones((3,3)),excludeSelf = True, sort = True):
    """ Returns a list of points which are neighbors of the given point.
        Neighbors are depicted as '1' in the given (Default 8-connected)"""
    shape = kernel.shape
    anchor = (int(shape[0]/2),int(shape[1]/2))
    points = []
    for c in range(shape[0]):
        for r in range(shape[1]):
            if kernel[c][r] != 0:
                if (not excludeSelf) or (not (anchor[0]==c and anchor[1]==r)) :
                    points.append([pt[0]+c-anchor[0],pt[1]+r-anchor[1]])
    if sort:
        sorted_points = []
        for pt in points:
            sorted_points.append((pt[0]**2+pt[1]**2,(pt[0],pt[1])))
        sorted_points.sort()
        points = []
        for pair in sorted_points:
            points.append(pair[1])
    return np.array(points)

#TODO?: Modify to accept numpy array of points, thereby allowing the function to solve multiple points at once
def mapToCanvas(pt,src_shape,dst_shape = (11*25.4,8.5*25.4),orient=True,stretch = False):
    """ Maps the given point in one image shape to its corresponding point in another shape.
        Options to automatically stretch and/or rotate the image in order to fill the destination shape
        Also returns scale and offset (in the case of no stretching) or scaleX and scaleY"""
    src_rows, src_cols = src_shape
    dst_rows, dst_cols = dst_shape

    if orient:
        if (dst_rows/dst_cols>1) and (src_rows/src_cols<1):
            pt = (pt[1],src_cols-pt[0])
            src_cols, src_rows = src_shape
        elif(dst_rows/dst_cols<1) and (src_rows/src_cols>1):
            pt = (src_rows-pt[1],pt[0])
            src_cols, src_rows = src_shape

    if stretch:
        pt_new = (pt[0]*dst_cols/src_cols,pt[1]*dst_rows/src_rows)
    else:
        scale = min(min(dst_rows,dst_cols)/min(src_rows,src_cols),max(dst_rows,dst_cols)/max(src_rows,src_cols))
        offset = ((dst_cols-scale*src_cols)/2,(dst_rows-scale*src_rows)/2)
        pt_new = (scale*pt[0]+offset[0],scale*pt[1]+offset[1])

    return pt_new

# TODO: Modify to accept updated LLT [[(x,y,W),...],...]
def drawLines(pts,img,thickness=3,showSteps=False):
    """ Draws the given LLT of points to the given image.
        Includes options for setting thickness or displaying each stroke individually"""
    for i in range(len(pts)):
        if len(pts[i])==1:
            cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),0,thickness*3)
            if showSteps:
                display(img)
        else:
            for c in range(len(pts[i])-1):
                cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),0,thickness)
            if showSteps:
                display(img)
    return img

def mapLLT(LLT,src_shape,dst_shape = (11*25.4,8.5*25.4),orient=True,stretch = False):
    out_pts = []
    for stroke in LLT:
        list_pts=[]
        for command in stroke:
            pt=mapToCanvas((command[1],command[0]),src_shape[:2],dst_shape,orient,stretch)
            list_pts.append(pt)
        out_pts.append(list_pts)
    return out_pts



def testLLT(LLT,scale = 2,paper_size = (11*25.4,8.5*25.4)):
    """	Displays the expected output of the given orders text file"""
    for stroke in LLT:
        for command_i in range(len(stroke)):
            command = stroke[command_i]
            stroke[command_i] = (scale*command[0],scale*command[1])
    drawnImg = drawLines(LLT,np.array(255*np.ones((int(paper_size[0]*scale),int(paper_size[1]*scale))),dtype='uint8'),2)
    display(drawnImg)

def testOrders(path='orders.text',scale = 2,paper_size = (11*25.4,8.5*25.4)):
    """	Displays the expected output of the given orders text file"""
    in_pts = []
    with open(path) as f:
        stroke = []
        # For each line in the file
        for line in f:
            if line == '\n' :
                in_pts.append(stroke)
                stroke = []
            else:
                coords = line.split(" ")
                stroke.append((scale*float(coords[0]),scale*float(coords[1])))

    drawnImg = drawLines(in_pts,np.array(255*np.ones((int(paper_size[0]*scale),int(paper_size[1]*scale))),dtype='uint8'),2)
    display(drawnImg)

def draw(pts,img,thickness=3):
    """this is what this does"""
    for i in range(len(pts)):
        if len(pts[i])==1:
            cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),0,thickness*3)
        else:
            for c in range(len(pts[i])-1):
                cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),0,thickness)

    return img

#TODO: Make this smarter, just give higher directory and recursive search
def getFileByName(fileName,path="../resources/images/input/"):
    return cv2.imread(path + fileName, cv2.IMREAD_UNCHANGED)