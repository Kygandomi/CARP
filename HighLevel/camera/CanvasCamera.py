import cv2
import numpy as np
from common import util
import time
import copy
from CameraException import *


class Camera(object):

    def __init__(self, port):
        self.port = port
        self.canvas_transformation_data = None
        self.canvas_to_dewarp_PT = None

        # # PMD AFTER FORCE PLATE
        # pts_gantry = np.float32([[400,400],[400,1900],[2400,400]])
        # pts_img = np.float32([[893,268],[893,795],[1606,268]])

        # Using a four point perspective transform

        # pts_gantry = np.float32([[200,200], [200, 2100],[2600, 2100],[2600,200]]) # [1280,600],[600,1280],[1800,1500]
        # pts_img = np.float32([[849,188],[854,831],[1670,827],[1671, 181]]) # [1219,322],[984,556],[1396,629]

        pts_gantry = np.float32([[200,400], [200, 2400],[2800, 2400],[2800,400]])
        pts_img = np.float32([[850,256],[853,930],[1738,926],[1740, 255]]) 

        self.img_to_gantryPT = cv2.getPerspectiveTransform(pts_img, pts_gantry)

        self.camera_capture = None
        self.open(port)

    def isOpened(self):
        """
        :return: Boolean if camera is properly connected to Python object or not.
        """
        if self.camera_capture is None:
            return False
        return self.camera_capture.isOpened()

    def open(self, port):
        """
        Attempts to create a connection to the camera. If it can't attach to port, it will look for other ports.
        Also specifies a frame height and width.
        :param port:
        :return:
        """
        if not isinstance(port,(list,tuple)):
            if not self.camera_capture is None:
                self.camera_capture.release()
            self.camera_capture = cv2.VideoCapture(port)   # value -> index of camera. My webcam was 0, USB camera was 1.
            if not self.camera_capture.isOpened():
                return False
            self.port = port
            self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            for i in range(0,4):    # Make a bunch of reads because sometimes first few images are all black
                self.read_camera()
            return True
        else:
            for p in port:
                if self.open(p):
                    return True
            return False


    @staticmethod
    def correct_image(src_imset, painted_imset):
        """
        Generates an array of images, containing area that must be painted by color.
        Canvas color is not provided in the image sets, and so is interpolated.

        src_imset: image decomp set containing array of color channels as bin images
        painted_imset: image decomp set containing array of color channels as bin images
        """

        print "Lets correct image"

        color_corrections = []
        canvas_corrections = None

        for image in range(len(painted_imset)):
            print "finding error..."

            error_img = cv2.bitwise_xor(painted_imset[image], src_imset[image])

            paint_color = cv2.bitwise_and(error_img, painted_imset[image])
            color_corrections.append(255-paint_color)

            paint_color = cv2.bitwise_and(error_img, src_imset[image])
            if canvas_corrections is not None:
                canvas_corrections += 255-paint_color
            else:
                canvas_corrections = 255-paint_color



        return color_corrections, canvas_corrections

    @staticmethod
    def dewarp(image):
        """
        This function applies a preset dewarping transform based on the physical properites of the camera
        :param image: The image that is to be undistorted
        :return: the image that has been dewarped (and slightly cropped)
        """
        # Should work on any computer if 1280x720 is explicitly set as resolution
        mtx =np.array([[  1.10631110e+03,   0.00000000e+00,   6.76280470e+02],
        [  0.00000000e+00,   1.10214590e+03,   2.61620659e+02],
        [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
        dist = np.array([[-0.47479333,  0.23125714,  0.01108992,  0.00123208, -0.04514544]])

        h,  w = image.shape[:2]

        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

        dewarped_canvas = cv2.undistort(image, mtx, dist, None, newcameramtx)

        x,y,w,h = roi

        dewarped_canvas = dewarped_canvas[y:y+h, x:x+w]

        dewarped_canvas = cv2.resize(dewarped_canvas, (0,0),fx=2,fy=2)

        return dewarped_canvas

    def read_camera(self):
        """
        Reads in the image from the camera of the port specified in the camera object.
        :return: returns the image read in from the camera as an opencv image
        """
        
        for i in range(3):
            self.camera_capture.read()
        s, img = self.camera_capture.read() # Attempt a read
        if s:    # frame captured without any errors
            # cv2.imwrite("camera_image.jpg",img) #save image
            return img
        else:
            raise CameraReadError("Unable to read from camera " + str(self.port))

    @staticmethod
    def order_points(pts):
        """Given an array of points defining a square, this will return them ordered
        such that will be ordered such that the first entry in the list is the top-left,
        the second entry is the top-right, the third is the bottom-right, and the fourth is the bottom-left. """

        rect = np.zeros((4, 2), dtype = "float32")
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def dewarp_to_gantry(self,pt):
        """
        For a specific point, applies the transform go go from a dewarped px to the gantry position
        """
        # return np.dot(self.img_to_gantryAT,[pt[0],pt[1],1])
        out = np.dot(self.img_to_gantryPT,[pt[0],pt[1],1])
        out = out/out[2]
        return [out[0],out[1]]

    def canvas_to_dewarp(self,pt):
        """
        Transforms a point from the canvas to the dewarped perspective transform
        """
        out = np.dot(self.canvas_to_dewarp_PT,[pt[0],pt[1],1])
        out = out/out[2]
        return [out[0],out[1]]

    def canvas_to_gantry(self, LLT):
        """
        For an LLT, converts the whole LLT from canvas space to gantry space
        """
        def canvas_to_gantry_pt(pt):
            return self.dewarp_to_gantry(self.canvas_to_dewarp(pt))

        out_pts = []
        for stroke in LLT:
            list_pts=[]
            for command in stroke:
                pt=canvas_to_gantry_pt([command[1],command[0]])
                list_pts.append([pt[0],pt[1],command[2]])
            out_pts.append(list_pts)
        return out_pts

    def four_point_transform(self, image):
        """
        Applies a stored, pre-generated 4-point transformation on an image
        """
        transform_matrix, maxWidth, maxHeight = self.canvas_transformation_data

        warped = cv2.warpPerspective(image, transform_matrix, (maxWidth, maxHeight))

        # return the warped image
        return warped

    def generate_transform(self, image=None, debug = False):
        """
        Generates the transform that must be used for this image.
        :param image: The image to use, will use camera capture if no image given
        :param debug: Verbose mode. Good for debugging any issues with this transform generator.
        :return: Returns nothing, stores transform data within this camera object.
        """
        if image is None:
            image = self.get_dewarped()

        # Make a deep copy for debugging later
        if debug: image_copy = copy.deepcopy(image)

        # Grayscale the image
        gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        # Blur the grayscale iamge
        gray_image = cv2.GaussianBlur(gray_image, (3,3), 0)

        if debug: util.display(gray_image, "gray image blurred")

        # close the image to provide our own noise reduction
        gray_image_closed = util.close_image(gray_image, kernel_radius = 15)

        if debug: util.display(gray_image_closed, "gray image, openned")

        # Apply an adaptive gaussian treshold to the image
        adaptive_thresholded = cv2.adaptiveThreshold(gray_image_closed,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

        if debug: util.display(adaptive_thresholded, "adaptive thresholded")

        # Now close the image, removing small areas of noise.
        adaptive_thresholded = util.close_image(gray_image, kernel_radius = 15)

        if debug: util.display(adaptive_thresholded, "addy treshed opened")

        # Apply canny edge detection to isolate edges.
        adaptive_thresholded_canny = cv2.Canny(adaptive_thresholded, 50,150, apertureSize = 3)

        if debug: util.display(adaptive_thresholded, "addy threshed, canny")

        # Blur the found thresholds.
        adaptive_thresholded_canny_blur = cv2.GaussianBlur(adaptive_thresholded_canny, (3,3), 0)

        if debug: util.display(adaptive_thresholded_canny_blur, "ady thresh canny blur")

        # Now we find the contours we will be applying.
        image, contours, other = cv2.findContours(adaptive_thresholded_canny_blur,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE) # Gather the contours
        long_contours = [] # Create an array for the long edges to be held

        for cnt in contours:
            if 60000<cv2.contourArea(cnt) < 5000000: # Tuned to prevent small contours, tuned for 6.75x8.5 as smallest canvas.
                long_contours.append(cnt) # Record any long contours
                if debug: print "area: ", cv2.contourArea(cnt)
                if debug: print "circ stat: ", cv2.minEnclosingCircle(cnt)
                if debug: cv2.drawContours(image_copy,[cnt],0,(0,255,127),2) # Draw those contours onto the image
                if debug: util.display(image_copy, str(time.time()))
        print "Long contours found: ", len(long_contours)

        # Sort the different contours discovered according to their contourArea.
        long_contours.sort(key=lambda x: cv2.contourArea(x), reverse=False)

        # Get the smaller transform generated.
        try:
            rect = cv2.minAreaRect(long_contours[0]) # Generate a rectangle based on the long contour surrounding the page
        except IndexError:
            util.display(image)
            raise CameraTransformError("Unable to get contours from camera image, check that camera image isn't washed out. \n \
            Debug mode was off, try turning it on to isolate the issue. Raising error in 3...2...1...")

        box = cv2.boxPoints(rect) # Generate a box-point object from the rectangle

        box = self.order_points(box) # Order the points so they were in proper order for transforms

        box = np.int0(box) # integer

        ordered_rect = self.order_points(box)

        (tl, tr, br, bl) = ordered_rect # top left, top right, bottom right, bottom left

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]],
            dtype = "float32")

        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(ordered_rect, dst)
        inv_M = cv2.getPerspectiveTransform(dst,ordered_rect)
        self.canvas_transformation_data = M, maxWidth, maxHeight
        self.canvas_to_dewarp_PT = inv_M

    def get_dewarped(self, image=None):
        """
        Dewarps an image.
        :param image: Will dewarp this image if it's an image, otherwise it will read from camera.
        :return: Dewarped image, either from the camera or from the given image
        """
        if image is None:
            return self.dewarp(self.read_camera()) # Attempts to make a new read from the camera.
        else:
            return self.dewarp(image) # Returns a dewarped image.
    
    def get_canvas(self, image = None):
        """
        From a camera object, retrieves the canvas.
        Takes in a dewarped image, or if no image is given it will take an image from the camera.
        :return:
        """

        if image is None:
            camera_image = self.get_dewarped() # Attempts to make a new read from the camera.
        else:
            camera_image = image # Accepts a dewarped image.

        if self.canvas_transformation_data is None: # If we have not generated a transformation yet (ie, first run)
            self.generate_transform(camera_image) # Generate the transformation

        # Either using the previously generated transform, or with our fresh new transform, do the transform+crop

        canvas_transformed_image = self.four_point_transform(camera_image)

        return canvas_transformed_image
