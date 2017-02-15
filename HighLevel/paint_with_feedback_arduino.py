from paint_with_arduino import serial_communication as ser_comm
from paint_with_arduino import paint_orders as PaintOrders

from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.skeleton.skeletonRecompose import *

from decomposition.decomp_color.decomp_color import *

from camera.CanvasCamera import Camera
from camera.CameraException import *

from common.util import *
from common import color_pallete

from time import sleep
import cv2

def paint_imageset(segments, painter, open_images = False):
	for index in range(len(segments)):
		print "Index ", index
		img = segments[index]
		if open_images: img = open_image(img)

		print "Fetching new brush"
		painter.getBrush(index)

		print "Recomposition"
		recomposer = skeletonRecomposer(img, [])
		LLT = recomposer.recompose()

		print "LLT to Paint as been saved to disc: ", LLT
		util.save(testLLT(LLT,3), "circle_from_llt")

		print "Painting LLT..."
		painter.Paint(LLT)

		print "LLT Completed."

	painter.returnToStart()
	sleep(3)
	print "First pass has been completed."

## SETUP COMMUNICATIONS
########################################################################################################################
print "Setup"

# Establish Serial Connection with the Arduino
baud = 115200
ports_list = ['COM8','COM3','/dev/tty.usbmodem1411', '/dev/tty.usbserial-A902U9B9', '/dev/cu.usbmodem1421']
could_connect = False

# Seek arduino connection
for i in range(len(ports_list)):
	port = ports_list[i]
	arduino_ser = ser_comm.serial_comms(port, baud)
	if arduino_ser.connect():
		print "Serial Comm Connected"
		could_connect = True
		break

# Comment back in when we have an actual serial port
if not could_connect :
	raise Exception('Could not connect...')

# Sleep to verify a solid connection
sleep(1)


## INITIALIZATION OF OBJECTS AND OTHER MISC SETUP REQUIREMENTS
########################################################################################################################
paint_routine = PaintOrders.paint_orders(arduino_ser)
palette = color_pallete.build("black white")
desiredImg = util.readImage("circle.png", "resources/images/input/")


cam = Camera(1)

read_img = cam.read_camera()

dewarp_img = cam.dewarp(read_img)
a, w, h = dewarp_img.shape

cam.generate_transform(dewarp_img)
img_to_show = cam.get_canvas(dewarp_img)

segmented_image, [colors,color_segments], [canvas,canvas_segment]  = decompose(desiredImg, 2,[], color_pallete.white)

paint_imageset(color_segments, paint_routine)


while 1:

	painting = cam.get_canvas(cam.dewarp(cam.read_camera()))

	rows, cols, _ = painting.shape

	# TODO Remember to remove this when we move to PMD and/or fix the transform issue
	M = np.float32([[1,0,12],[0,1,21]])
	painting = cv2.warpAffine(painting,M,(cols,rows))


	segmented_image_act, [_,color_segments_src], [_,_] = decompose(desiredImg, 0,palette, color_pallete.white)

	_, [_,color_segments_act], [_,_] = decompose(painting, 0,palette, color_pallete.white)

	# Resize each segment
	for elt in range(0, len(color_segments_src)):
		color_segments_src[elt] = resize_with_buffer(color_segments_src[elt], color_segments_act[elt])

	# Generate correction images
	correction_segments, canvas_corrections = cam.correct_image(color_segments_src,color_segments_act)

	paint_imageset(correction_segments, paint_routine, open_images = True)