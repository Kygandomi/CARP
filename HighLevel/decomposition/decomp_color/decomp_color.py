from common import util
import numpy as np
from scipy.cluster.vq import kmeans,vq
import math
from colormath.color_objects import sRGBColor, LabColor 
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1994
from itertools import permutations, combinations, combinations_with_replacement

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
    indeces = []

    if (sz > 0) and n_points>0:
        colors_lab, pallete_lab = convert(colors, pallete)
        colors_x, indeces = classify(colors_lab, pallete_lab)
        # colors = pallete

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
    indeces = list(indeces)
    canvas_index = indeces.pop(0)
    return [image, [np.delete(colors,0,axis=0),bin_images,indeces], [canvas_color,bin_image, canvas_index]]


def color_quantize(image, n_colors=2, size_to=300):
    if size_to>0:
        small_img = util.resize(image,size_to)
    else:
        raise ValueError

    pixel = np.reshape(small_img,(small_img.shape[0]*small_img.shape[1],3))

    # performing the clustering
    centroids,_ = kmeans(np.float32(pixel),n_colors,iter=200)


    return np.uint8(centroids)

def rgb2lab ( inputColor ) :
    color_rgb = sRGBColor(inputColor[0], inputColor[1], inputColor[2])
    color_lab = convert_color(color_rgb, LabColor)
    return color_lab

def convert(rgb_img, rgb_paint):
    img_lab = []
    paint_lab = []

    for color in rgb_img:
        color_lab = rgb2lab(color)
        img_lab.append(color_lab)

    for color in rgb_paint:
        color_lab = rgb2lab(color)
        paint_lab.append(color_lab)

    return img_lab, paint_lab

def find_max_error(img_colors, paint_colors):
    max_error = 0
    for index in range(len(img_colors)):
        delta_e = delta_e_cie1994(img_colors[index], paint_colors[index])
        if delta_e > max_error:
            max_error = delta_e

    return max_error

def classify(img_colors, paint_colors):

    # Get the number of paint colors and kmeans colors
    num_colors_pallete = len(paint_colors) # N 
    num_colors_kmeans = len(img_colors) # R

    # Get all possible combinations
    sorted_combinations = combinations(range(num_colors_pallete), num_colors_kmeans)
    unique_permutations = set()
    
    for combo in sorted_combinations:
        for p in permutations(combo): 
            unique_permutations.add(p)

    min_combo = []
    min_error = find_max_error(img_colors, paint_colors)
    for combo in unique_permutations:
        temp_paint_combo = []
        for i in range(len(combo)):
            temp_paint_combo.append(paint_colors[combo[i]])

        # print "paint combo", temp_paint_combo
        err = find_max_error(img_colors , temp_paint_combo)

        if err < min_error:
            min_error = err
            min_combo= combo

    return paint_colors, min_combo

    
    # closest_match = []
    # for img_color in img_colors:
    #     smallest_i = -1
    #     smallest_deltaE = 9999999999
    #     # print "******"
    #     # print "For img_color: ", img_color

    #     for pos in range(len(paint_colors)):
    #         paint_color = paint_colors[pos]
    #         delta_e = delta_e_cie1994(img_color, paint_color)
    #         # print "diff: ", delta_e 
    #         # print "paint_color ", paint_color

    #         if delta_e < smallest_deltaE: 
    #             smallest_deltaE = delta_e
    #             smallest_i = pos

    #     closest_match.append(smallest_i)
    # print "closest_match", closest_match
    # return paint_colors, closest_match


def classify2(img_colors, paint_colors):
    # Map old img_colors to their closest color in paint_colors
    colors = np.array(paint_colors)
    qnt,_ = vq(img_colors,paint_colors)

    return colors[qnt], qnt

def remove_canvas(img_colors,canvas_color = [255,255,255]):
    # Find index of img_color that most closely matches canvas color
    best_index = np.argmin(np.linalg.norm(np.array(canvas_color)-np.array(img_colors),axis=1))
    # Remove that color from list of required paint colors
    img_colors=np.delete(img_colors,best_index,axis=0)

    return img_colors