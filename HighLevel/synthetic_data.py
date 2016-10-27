#!/usr/bin/env python
#http://www.scipy-lectures.org/advanced/image_processing/auto_examples/plot_synthetic_data.html#example-plot-synthetic-data-py

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import cv2
from scipy.ndimage import filters
from skimage import filter

#randomize picture instead of loading it
#np.random.seed(1)
#n = 30
#l = 256
#im = np.zeros((l, l))
#points = l*np.random.random((2, n**2))
#im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
#im = ndimage.gaussian_filter(im, sigma=l/(4.*n))



im3 = cv2.imread('lena.jpg',0)
#im3 = np.invert(im4)
im2 = cv2.adaptiveThreshold(im3, 255, cv2.ADAPTIVE_THRESH_MEAN_C,\
	cv2.THRESH_BINARY,15,2)
im1 = filters.gaussian_filter(im2, 3)

im = ndimage.grey_dilation(im1, size = (5,5))

#mean thresholding
mask = im > im.mean()

#otsu thresholding - distinguishes background
#val = filter.threshold_otsu(im)
#mask = im < val

label_im, nb_labels = ndimage.label(mask)

plt.figure(figsize=(9,3))

plt.subplot(131)
plt.imshow(im3, cmap=plt.cm.gray)
plt.axis('off')
plt.subplot(132)
plt.imshow(mask, cmap=plt.cm.gray)#im
plt.axis('off')
plt.subplot(133)
imfinal = ndimage.grey_erosion(label_im, size=(5,5))
plt.imshow(imfinal)#label_im, cmap=plt.cm.spectral
plt.axis('off')


plt.subplots_adjust(wspace=0.02, hspace=0.02, top=1, bottom=0, left=0, right=1)
plt.show()