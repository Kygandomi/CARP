from common import util
import numpy as np
import cv2
from scipy.cluster.vq import kmeans,vq

#################################################################################

def decompose(image,n_points,pallete = [], canvas_color = [255,255,255]):
    sz = len(pallete)
    paint_colors=[]
    # Just use pallete
    if n_points < 1:
        paint_colors.extend(pallete)
        if canvas_color in paint_colors:
            paint_colors.remove(canvas_color)
    else:
        paint_colors = color_quantize(image,n_points)
        paint_colors = remove_canvas(paint_colors,canvas_color)

    colors = np.concatenate((np.array([canvas_color]),np.array(paint_colors)))

    # image = util.open_image(util.close_image(image))

    pixel = np.reshape(image,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors)
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))

    if (sz > 0) and n_points>0:
        colors = classify(colors,pallete)

    image = colors[centers_idx]
    image = np.uint8(image)

    bin_images = [] # The 1-color images.

    for index in range(0, len(colors)):
        # Create a deep copy of the image
        bin_image = 255-np.zeros((image.shape[0],image.shape[1],1), np.uint8)
        #bin_image[np.where((image == paint_colors[index]).all(axis = 2))] = [0]
        bin_image[np.where((centers_idx == index))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.
    
    bin_image = bin_images.pop(0)
    return [image, [np.delete(colors,0,axis=0),bin_images], [canvas_color,bin_image]]

#################################################################################

def color_quantize(image, n_colors=2, size_to=300):
    if size_to>0:
        small_img = util.resize(image,size_to)

    # small_img = cv2.cvtColor(np.float32(small_img)*1./255, cv2.COLOR_BGR2LAB)

    pixel = np.reshape(small_img,(small_img.shape[0]*small_img.shape[1],3))

    # performing the clustering
    centroids,_ = kmeans(np.float32(pixel),n_colors,iter=200)

    # out  = np.uint8(np.array([centroids]))
    # cv2.cvtColor(np.array([centroids]), cv2.COLOR_LAB2BGR,out)
    # centroids = out[0]

    # L = centroids[:,:,0]*100/255
    # a = centroids[:,:,1]+128
    # b = centroids[:,:,2]+128

    # centroids = np.uint8(cv2.merge((L,a,b)))

    return np.uint8(centroids)

def classify(img_colors, paint_colors):
    # Map old img_colors to their closest color in paint_colors
    
    colors = np.array(paint_colors)

    # img_colors = cv2.cvtColor(np.array([img_colors],np.uint8), cv2.COLOR_BGR2LAB)[0]
    # paint_colors = cv2.cvtColor(np.array([paint_colors],np.uint8), cv2.COLOR_BGR2LAB)[0]

    qnt,_ = vq(img_colors,paint_colors)

    # return list of new paint colors plus canvas color
    return colors[qnt]

def remove_canvas(img_colors,canvas_color = [255,255,255]):
    # Find index of img_color that most closely matches canvas color
    best_index = np.argmin(np.linalg.norm(np.array(canvas_color)-np.array(img_colors),axis=1))
    # Remove that color from list of required paint colors
    img_colors=np.delete(img_colors,best_index,axis=0)

    return img_colors