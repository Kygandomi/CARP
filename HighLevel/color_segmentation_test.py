from decomposition.color_segmentation.color_segmentation import color_segment
from common import util
# RGB for yellow: 255, 236, 38
blue_green_yellow = [[255,0,0],[0,255,0],[0,233,255]]
blue_green_red = [[255,0,0],[0,255,0],[0,0,255]]
random_test = [[188,49,156],[188,135,49],[27,163,27],[0,174,255],[15,15,175],[113,252,139]]
colors, color_segments, segmented_image = color_segment("sunflower_color.png", random_test)


for image in color_segments:
    util.display(image)