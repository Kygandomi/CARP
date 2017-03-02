from color_segmentation import color_segment
from common import util
# RGB for yellow: 255, 236, 38

blue = [255,0,0]
green = [0,255,0]
yellow = [0,233,255]
red = [0,0,255]
white = [255,255,255]
black = [0,0,0]

random_test = [[188,49,156],[188,135,49],[27,163,27],[0,174,255],[15,15,175],[113,252,139]]

image = util.getFileByName("boat.png","../../resources/images/input/")


colors, color_segments, segmented_image = color_segment(image, [yellow, red, blue, white])

for image in color_segments:
    util.display(util.open_image(image), "opened")
    # util.save(util.open_image(image), "image")