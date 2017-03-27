import numpy as np
import cv2

def display(img, name="img"):
    """
    Desplays img in a new window, waits until space is pressed.
    """
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def displayarray(imgs, name="imageset_image"):
    """
    Display an array of images
    :param imgs: image array to display from
    :param name: name they will be shown with
    :return:
    """
    for img in imgs:
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def save(img, name="test_image"):
    """
    Saves an image. A directory can be specified in name, eg: where/pictures/go/picture1
    Don't give it a filetype in name.
    """
    cv2.imwrite(name+".png", img)

def output(img,name="output"):
    """
    Saves and displays an image.
    """
    save(img,name)
    display(img,name)


def resize(img,max_dim=1000):
    """
    Given an image, this function will resize the image such that it's greatest dimension is max_dim.
    """
    rows, cols, _ = img.shape

    if rows == max_dim or cols==max_dim:
        return img

    method = cv2.INTER_CUBIC
    if max(rows,cols)>max_dim:
        method = cv2.INTER_AREA

    if rows<cols:
        return cv2.resize(img,(max_dim,max_dim*rows/cols),interpolation = method)
    else:
        return cv2.resize(img,(max_dim*cols/rows,max_dim),interpolation = method)


def rotate_image(mat, angle, padding_color = (255,255,255)):
    """
    Returns a rotated image, rotated by the given angle.
    :param mat: The image to rotate
    :param angle: The angle (in degrees) to rotate
    :param padding_color:
    :return:
    """
    height, width = mat.shape[:2]
    image_center = (width/2, height/2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, -angle, 1.)

    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h), borderValue=padding_color)
    return rotated_mat


def resize_with_buffer(ideal, actual, allowRotaton=True, padding_color = [255,255,255]):
    """
    Reshapes an ideal image to suit the dimensions of an actual image.

    :param ideal: The ideal image that needs to be reshaped
    :param actual: The actual image.
    :param: allowRotation: Whether or not we're going to allow it to rotate to preserve detail.
    :param: padding_color: The color that is going to fill in the area created when resizing.
    :return: The new image, resized and with buffer and rotation if neccecary and selected
    """
    h_perf, w_perf, _ = ideal.shape
    h_actual, w_actual, _ = actual.shape

    perf_ratio = float(h_perf)/float(w_perf)
    actual_ratio =float(h_actual)/float(w_actual)

    buff = 0,0,0,0

    # If it's acceptable to rotate the image
    if allowRotaton:
        # If one is portrait and the other is landscape, then we should rotate.
        if ((perf_ratio > 1) and (actual_ratio < 1)) or ((perf_ratio < 1) and (actual_ratio > 1)):
            print "Rotating image in order to match portrait/landscapeness."
            ideal = rotate_image(ideal, 90, padding_color=padding_color)

    h_perf, w_perf, _ = ideal.shape
    perf_ratio = float(h_perf)/float(w_perf)

    if perf_ratio > actual_ratio:
        odd = False
        if w_actual %2 == 1: # If we have an odd number of pixels
            odd = True
        buff_val = ((h_perf/actual_ratio)-w_perf) /2
        buff = 0,0, int(buff_val), int(buff_val) + int(odd)
    elif perf_ratio < actual_ratio:
        odd = False
        if w_actual %2 == 1: # If we have an odd number of pixels
            odd = True
        buff_val = ((w_perf*actual_ratio)-h_perf) /2
        buff = int(buff_val), int(buff_val) + int(odd), 0, 0 # int(buff_val), int(buff_val) + int(odd)

    top, bottom, left, right = buff

    img = cv2.copyMakeBorder(ideal, top, bottom, left, right, cv2.BORDER_CONSTANT,value=padding_color)
    return cv2.resize(img, (w_actual, h_actual))


def circleKernel(radius,thickness = -1):
    """ Return a kernal representing a circle with the given radius and thickness (in pixels)"""
    brush = cv2.circle(np.zeros((radius*2+1,radius*2+1)),(radius,radius),radius,1,thickness).astype('uint8')
    return brush

def overlay(back,front,backcolor=127,frontcolor=0):
    img = back.copy()
    img[np.where(back==0)]=backcolor
    img[np.where(front==0)]=frontcolor
    return img

def getPoints(img,color=255):
    """ Return a list of points in a grayscale image which are of the given value. Default 255 (black)"""
    # filter the image to a numpy array that contains all pixels of the color "color"
    pts = np.array(np.where(img == color))
    real_pts = []

    for j in range(len(pts[0])):
        real_pts.append((pts[0][j],pts[1][j]))
    return real_pts

def getNeighborPoints(pt,kernel = np.ones((3,3)),excludeSelf = True, sort = True):
    """ Returns a list of points which are neighbors of the given point.
    Neighbors are depicted as '1' in the given kernel (Default 8-connected)"""
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
def mapToCanvas(pt,src_shape,dst_shape = (8.5*25.4,11*25.4),orient=True,stretch = False):
    """ Maps the given point in one image shape to its corresponding point in another shape.
    Options to automatically stretch and/or rotate the image in order to fill the destination shape
    Also returns scale and offset (in the case of no stretching) or scaleX and scaleY"""
    src_rows, src_cols = src_shape
    dst_rows, dst_cols = dst_shape

    dst_rows = float(dst_rows)
    dst_cols = float(dst_cols)
    src_rows = float(src_rows)
    src_cols = float(src_cols)

    if orient:
        #dst is portrait and src is landscape
        if (dst_rows/dst_cols>1) and (src_rows/src_cols<1):
            #rotate 90 degrees right
            pt = (src_rows-pt[1],pt[0])
            src_cols, src_rows = src_shape
        # dst is landscape and src is landscape
        elif(dst_rows/dst_cols<1) and (src_rows/src_cols>1):
            #rotate 90 degrees left
            pt = (pt[1],src_cols-pt[0])
            src_cols, src_rows = src_shape

    if stretch:
        pt_new = (pt[0]*dst_cols/src_cols,pt[1]*dst_rows/src_rows)
    else:
        scale = min(min(dst_rows,dst_cols)/min(src_rows,src_cols),max(dst_rows,dst_cols)/max(src_rows,src_cols))
        offset = ((dst_cols-scale*src_cols)/2,(dst_rows-scale*src_rows)/2)
        pt_new = (scale*pt[0]+offset[0],scale*pt[1]+offset[1])

    return pt_new

# TODO: Modify to accept updated LLT [[(x,y,W),...],...]
def drawLines(pts,img,thickness=3,color=0,showSteps=False):
    """ Draws the given LLT of points to the given image.
    Includes options for setting thickness or displaying each stroke individually"""
    for i in range(len(pts)):
        if len(pts[i])==1:
            cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),thickness,color,-1)
            if showSteps:
                display(img)
        else:
            for c in range(len(pts[i])-1):
                cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),color,thickness)
            if showSteps:
                display(img)
    return img

def mapLLT(LLT,src_shape,dst_shape = (8.5*25.4,11*25.4),orient=True,stretch = False):
    """
    Maps an LLT from a source shape onto a destination shape
    (So, from one source that generated the LLT such as an image, onto a canvas for example)
    :return:
    """
    out_pts = []
    for stroke in LLT:
        list_pts=[]
        for command in stroke:
            pt=mapToCanvas((command[1],command[0]),src_shape[:2],dst_shape,orient,stretch)
            list_pts.append(pt)
        out_pts.append(list_pts)
    return out_pts

def drawLLT(LLT,img,thickness=2,color=0):
    """ Returns the expected output of the given set of orders"""
    lines = []
    for stroke in LLT:
        pt_list = []
        for command_i in range(len(stroke)):
            command = stroke[command_i]
            pt = (command[1],command[0])
            pt_list.append(pt)
        lines.append(pt_list)
    drawnImg = drawLines(lines,img,thickness,color)
    return drawnImg


def testLLT(LLT,scale = 1,paper_size = (8.5*25.4,11*25.4),thickness=2,color=0):
    """	Displays the expected output of the given orders text file"""
    if not isinstance(color,(list,tuple)):
        img = np.array(255*np.ones((int(paper_size[0]*scale),int(paper_size[1]*scale))),dtype='uint8')
    else:
        img = np.array(255*np.ones((int(paper_size[0]*scale),int(paper_size[1]*scale),len(color))),dtype='uint8')

    lines = []
    for stroke in LLT:
        pt_list = []
        for command_i in range(len(stroke)):
            command = stroke[command_i]
            pt = (scale*command[1],scale*command[0])
            pt_list.append(pt)
        lines.append(pt_list)
    drawnImg = drawLines(lines,img,thickness,color)
    return drawnImg

def loadLLT(fname = 'orders.txt'):
    """
    Load in an LLT from a text file.
    """
    LLT=[]
    with open(fname) as f:
        stroke = []
        for line in f:
            if line == '\n' :
                LLT.append(stroke)
                stroke = []
            else:
                coords = line.split(" ")
                stroke.append([float(coords[0]),float(coords[1]),float(coords[2])])
    return LLT

def saveLLT(LLT,fname = 'orders.txt'):
    """
    Save the LLT directly to the specified text file.
    """
    with open(fname,'w') as f:
        for path_i in range(len(LLT)):
            path = LLT[path_i]
            for pt_i in range(len(path)):
                pt=path[pt_i]
                f.write(str(pt[0]) + ' '+ str(pt[1]) + ' ' + str(pt[2]) + ' \n')
            f.write('\n')

def arrangeLLT(LLT):
    """
    Arrange an LLT so that when using naive painters, they will be better arranged for fast painting.
    """
    oldLLT=list(LLT)
    newLLT=[]

    newLLT.append(oldLLT.pop(0))
    last_pt = newLLT[len(newLLT)-1][len(newLLT[0])-1][:2]

    while len(oldLLT)>0:
        reverse = False
        min_i = 0
        min_dist = -1
        for i in range(len(oldLLT)):
            dist = np.linalg.norm(np.array(last_pt)-np.array(oldLLT[i][0][:2]))
            if (min_dist == -1) or dist<min_dist:
                min_dist=dist
                min_i=i
                reverse=False

            dist = np.linalg.norm(np.array(last_pt)-np.array(oldLLT[i][len(oldLLT[i])-1][:2]))
            if dist<min_dist:
                min_dist=dist
                min_i=i
                reverse=True

        last_stroke = oldLLT.pop(min_i)
        if reverse:
            last_stroke.reverse()
        newLLT.append(last_stroke)
        last_pt = last_stroke[len(last_stroke)-1][:2]

    return newLLT


def reduceLLT(LLT,min_dist):
    """
    Reduces a set of indtructions to remove datapoints that are too close to have notable effects on the end result.
    """
    prev_pt = [-10000,-10000]

    out_pts = []
    for path_i in range(len(LLT)):
        path = LLT[path_i]
        list_pts=[]
        for pt_i in range(0,len(path)-1,1):
            pt=path[pt_i]
            if np.linalg.norm(np.array(prev_pt[:2])-np.array(pt[:2]))>min_dist:
                prev_pt = pt
                list_pts.append(pt)
        list_pts.append(path[len(path)-1])
        out_pts.append(list_pts)

    return out_pts


def testOrders(path='orders.txt',scale = 2,paper_size = (8.5*25.4,11*25.4)):
    """	Displays the expected output of the given orders text file"""
    testLLT(loadLLT(path),scale,paper_size)


def draw(pts,img,thickness=3):
    """this is what this does"""
    for i in range(len(pts)):
        if len(pts[i])==1:
            cv2.circle(img,(int(pts[i][0][0]),int(pts[i][0][1])),0,thickness*3)
        else:
            for c in range(len(pts[i])-1):
                cv2.line(img,(int(pts[i][c][0]),int(pts[i][c][1])),(int(pts[i][c+1][0]),int(pts[i][c+1][1])),0,thickness)
    return img


def readImage(fileName,path="resources/images/input/",type_flag = cv2.IMREAD_COLOR,size = 1000):
    read_file =  cv2.imread(path + fileName, type_flag)
    if read_file is None:
        raise ValueError('Error in attempt to read file. Are you sure the file is there?')
    if size<=0:
        return read_file
    return resize(read_file,size)


#TODO: Make this smarter, just give higher directory and recursive search
def getFileByName(fileName,path="resources/images/input/"):
    read_file =  cv2.imread(path + fileName, cv2.IMREAD_UNCHANGED)
    if read_file is None:
        raise ValueError('Error in attempt to read file. Are you sure the file is there?')
    return read_file


#TODO: Make this smarter, just give higher directory and recursive search
def getFileByNameNoAlpha(fileName,path="resources/images/input/"):
    read_file =  cv2.imread(path + fileName, cv2.IMREAD_COLOR)
    if read_file is None:
        raise ValueError('Error in attempt to read file. Are you sure the file is there?')
    return read_file


def getFileByName_8UC1(fileName,path="resources/images/input/"):
    read_file =  cv2.imread(path + fileName, cv2.CV_8UC1)
    if read_file is None:
        raise ValueError('Error in attempt to read file. Are you sure the file is there?')
    return read_file


# TODO Rename this so it's not misleading, also teach Odell how to properly do life
def open_image(img, kernel_radius = 5, itera = 1):
    """Assumes image has black image on white background"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_radius,kernel_radius))
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=itera)


def close_image(img, kernel_radius = 5, itera = 1):
    """Assumes image has black image on white background"""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_radius,kernel_radius))
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=itera)