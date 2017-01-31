from grayscale_segmentation import grayscale_segment
from common import util

image = util.getFileByName("grayscale_test.png", "../../resources/images/input/")

image_root, image_set = grayscale_segment(image, 5)

util.display(image_root)

for image in image_set:
    util.display(image)