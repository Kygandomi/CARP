from common import util
import numpy as np
import cv2
from scipy.cluster.vq import kmeans,vq

def color_quantize(image, n_colors=2, size_to=200):
    if size_to>0:
        small_img = util.resize(image,size_to)
    pixel = np.reshape(np.float32(small_img),(small_img.shape[0]*small_img.shape[1],3))

    # performing the clustering
    centroids,_ = kmeans(pixel,n_colors,iter=100)

    return np.uint8(centroids)

def classify(img_colors, paint_colors):
    # Map old img_colors to their closest color in paint_colors
    colors = np.array(paint_colors)
    qnt,_ = vq(img_colors,paint_colors)

    # return list of new paint colors plus canvas color
    return colors[qnt]

def remove_canvas(img_colors,canvas_color = [255,255,255]):
    # Find index of img_color that most closely matches canvas color
    best_color = np.argmin(np.linalg.norm(np.array(canvas_color)-np.array(img_colors),axis=1))
    # Remove that color from list of required paint colors
    img_colors=np.delete(img_colors,best_color,axis=0)

    return img_colors