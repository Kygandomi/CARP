from grayscale_segmentation import grayscale_segment
from HighLevel.common import util

image_root, image_set = grayscale_segment("skull.png", 4)

util.display(image_root)

for image in image_set:
    util.display(image)