import cv2
import numpy as np
from common import util
from common import color_pallete
import copy
from CameraException import *
from color_segmentation import color_segment



def dewarp(image):

    mtx = np.array([[  4.93988251e+03 ,  0.00000000e+00 ,  6.67427894e+02],
 [  0.00000000e+00 ,  5.29553206e+03  , 4.49712265e+02],
 [  0.00000000e+00 ,  0.00000000e+00 , 1.00000000e+00]])

    dist = np.array([[ -1.10157126e+01 ,  1.27727231e+02 , -1.25121362e-02  ,-4.19927722e-03,
   -1.67823487e+02]])


    gray = image

    h,  w = gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    dewarped_canvas = cv2.undistort(gray, mtx, dist, None, newcameramtx)

    x,y,w,h = roi

    dewarped_canvas = dewarped_canvas[y:y+h, x:x+w]

    return dewarped_canvas

def correct_image(src_imset, painted_imset):
    """
    Generates an array of images, containing area that must be painted by color.
    Canvas color is not provided in the image sets, and so is interpolated.

    src_imset: image decomp set containing array of color channels as bin images
    painted_imset: image decomp set containing array of color channels as bin images
    """

    color_corrections = []
    canvas_corrections = []

    for image in range(len(painted_imset)):

        error_img = cv2.bitwise_xor(painted_imset[image], src_imset[image])

        paint_color = cv2.bitwise_and(error_img, painted_imset[image])
        color_corrections.append(paint_color)

        paint_color = cv2.bitwise_and(error_img, src_imset[image])
        canvas_corrections.append(paint_color)

    return color_corrections, canvas_corrections


# warped_canvas = cv2.imread("CameraFeedback/1.png", cv2.IMREAD_UNCHANGED)
warped_picture = cv2.imread("CameraFeedback/flask_mod.png", cv2.IMREAD_COLOR)

src_img = util.getFileByNameNoAlpha("flask.png", "../resources/images/input/") #cv2.imread("CameraFeedback/fake.png", cv2.IMREAD_COLOR)



# dewarped_canvas = dewarp(warped_canvas)
# dewarped_picture = dewarp(warped_picture)
dewarped_picture = warped_picture
# src_img = dewarp(src_img)



_, h, w = warped_picture.shape

xinit = 430
xlim = 370
yinit = 130
ylim = 660

# dewarped_canvas = dewarped_canvas[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
# segmented_picture = dewarped_picture[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
# src_img = src_img[yinit:h-ylim, xinit:w-xlim] # NOTE: its img[y: y + h, x: x + w]
segmented_picture = dewarped_picture

util.display(segmented_picture)
util.display(src_img)


palette = color_pallete.buildPallete("blue   green")


colors, color_segments, segmented_image = color_segment(dewarped_picture, palette)
colors_src, color_segments_src, segmented_image_src = color_segment(src_img, palette)

paint_color_corrections, paint_canvas_corrections = correct_image(color_segments_src, color_segments)

for elt in paint_color_corrections:
    util.display(elt)

for elt in paint_canvas_corrections:
    util.display(elt)

#  util.display(get_canvas(None, dewarped_canvas)) # Shit's broken - Odell needs LED's
