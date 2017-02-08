from common import util
import numpy as np
import cv2
from scipy.cluster.vq import kmeans,vq

def color_quantize(image, n_colors=2):

    pixel = np.reshape(np.float32(image),(image.shape[0]*image.shape[1],3))

    # performing the clustering
    centroids,_ = kmeans(pixel,n_colors) # six colors will be found
    
    print centroids

    return centroids