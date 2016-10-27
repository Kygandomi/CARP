#!/usr/bin/env python

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import filters
from scipy import ndimage

img = cv2.imread('lena.jpg',0)
img = cv2.medianBlur(img,5)

ret,th1 = cv2.threshold(img,123,255,cv2.THRESH_BINARY)
th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY,11,2)
th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)
th4 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
	cv2.THRESH_BINARY,15,2)
th5 = filters.gaussian_filter(img, 3)
ret,th6 = cv2.threshold(th5, 110, 255, cv2.THRESH_BINARY)
th7 = cv2.adaptiveThreshold(th5,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,15,2)


img2 = th6 > th6.mean()
label_im, nb_labels = ndimage.label(img2)

thresh = th6[0,0]
mask = th6 != thresh
label_m, bn_labels = ndimage.label(mask)



thresh2 = th7[0,0]
mask2 = th7 != thresh2
label_m2, bn_labels2 = ndimage.label(mask2)

#not being used
mask3 = th7 == thresh2
label_im2, nb_labels2 = ndimage.label(mask3)


titles = ['Original Image', 'Adaptive Thresholding',
            'Gaussian Blur', 'Gaussian Blur + Binary Thresholding', 
            'Black Feature Detection', 'White Feature Detection',
            'Gaussian Blur + Adaptive Thresholding', 'Black Feature Detection', 'White Feature Detection']
images = [img,th2, th5, th6, label_m, label_im, th7, label_m2, label_im2]

for i in xrange(4):
    plt.subplot(3,3,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.subplot(3,3,5),plt.imshow(images[4])
plt.title(titles[4])
plt.xticks([]),plt.yticks([])
plt.subplot(3,3,6),plt.imshow(images[5])
plt.title(titles[5])
plt.xticks([]),plt.yticks([])

plt.subplot(3,3,7),plt.imshow(images[6], 'gray')
plt.title(titles[6])
plt.xticks([]),plt.yticks([])
plt.subplot(3,3,8),plt.imshow(images[7])
plt.title(titles[7])
plt.xticks([]),plt.yticks([])

plt.subplot(3,3,9),plt.imshow(images[8])
plt.title(titles[8])
plt.xticks([]),plt.yticks([])
plt.show()
