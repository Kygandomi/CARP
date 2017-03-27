from Highlevel.common.util import *

#Fills in an area of black with vertical lines

class verticalRecompose(object):

    def __init__(self, image, args):
        """
        :param image:
        :param args: [brush_size]
        :return:
        """
        self.desiredImage = image
        self.brush_size = args[0]

    def recompose(self):
        """
        Recomposes the image using a linear fill method.
        :return:
        """
        #dilate the image the radius of the brush
        kernel = np.ones((self.brush_size,self.brush_size), np.uint8)
        dilateImg = cv2.dilate(self.desiredImage,kernel,iterations = 1)

        #find height and width of image
        height, width, channels = dilateImg.shape
        startPoints = []
        endPoints = []

        line = False
        stroke = False

        #find start and end points based on the brush size
        for y in range(0, height):
            if not stroke:
                for x in range(0, width):
                    if 0 in dilateImg[x,y] and line==False:
                        startPoints.append([x,y])
                        stroke = True
                        newy = y + (2*self.brush_size)
                        line = True
                    if line==True and 0 not in dilateImg[x,y]:
                        endPoints.append([x-1,y])
                        line = False
            elif newy <= y:
                stroke = False


        canvasImg = np.zeros((height, width, channels), np.uint8) #make new canvas the size of the original image
        canvasImg.fill(255) #fill with white

        for element in range(0, len(startPoints)-1):
            canvasImg[startPoints[element][0], startPoints[element][1]] = (0,0,0,255)
            canvasImg[endPoints[element][0], endPoints[element][1]] = (0,0,0,255)

        save(canvasImg, "test_image") #displays start and end points only

        #create txt document of the start/end of each stroke
        pixelToMM = (8.5*25.4)/width
        orders = open("VertFillOrders.txt", 'w') #store points
        for element in range(0, len(startPoints)-1):
            orders.write(str(startPoints[element][0]*pixelToMM)+' '+str(startPoints[element][1]*pixelToMM)+' '+str(endPoints[element][0]*pixelToMM)+' '+str(endPoints[element][1]*pixelToMM) +'\n')
        orders.close()