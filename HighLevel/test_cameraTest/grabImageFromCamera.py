from cv2 import *

def get_image(camera_value):
	cam = VideoCapture(camera_value)   # value -> index of camera. My webcam was 0, USB camera was 1.
	s, img = cam.read()
	if s:    # frame captured without any errors
	    #namedWindow("cam-test",CV_WINDOW_AUTOSIZE)
	    imshow("cam-test",img)
	    waitKey(0)
	    destroyWindow("cam-test")
	    imwrite("camera_image.jpg",img) #save image

get_image(1)