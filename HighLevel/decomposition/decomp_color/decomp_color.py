from common import util
import numpy as np
from scipy.cluster.vq import kmeans,vq
import math
import cv2
from colormath.color_objects import sRGBColor, LabColor 
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from itertools import permutations, combinations, combinations_with_replacement
from copy import deepcopy

def decomposeOLD(image,n_points,pallete = [], canvas_color = [255,255,255]):
    sz = len(pallete)
    paint_colors=[]
    indeces = []
    canvas_index = -1;
    # Just use pallete
    if n_points < 1:
        paint_colors.extend(pallete)
        if canvas_color in paint_colors:
            paint_colors,canvas_index = remove_canvas(paint_colors,canvas_color)
            indeces = range(sz)
            indeces.pop(canvas_index)
            indeces.insert(0,canvas_index)
    else:
        paint_colors = color_quantize(image,n_points)
        paint_colors,_ = remove_canvas(paint_colors,canvas_color)

    colors = np.concatenate((np.array([canvas_color]),np.array(paint_colors)))

    # image = util.open_image(util.close_image(image))
    pixel = np.reshape(image,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors)
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))

    if (sz > 0) and n_points>0:
        colors_lab, pallete_lab = convert(colors, pallete)
        colors_x, indeces = classify(colors_lab, pallete_lab)
        pallete = np.array(pallete)
        colors = pallete[indeces]
        
        # colors = np.array(elementsOf(pallete,indeces));
    elif sz>0:
        indeces = range(sz)
    else:
        indeces = range(n_points)

    image = colors[centers_idx]
    image = np.uint8(image)

    bin_images = [] # The 1-color images.

    for index in range(0, len(colors)):
        # Create empty image
        bin_image = 255-np.zeros((image.shape[0],image.shape[1],1), np.uint8)
        bin_image[np.where((centers_idx == index))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.
    
    bin_image = bin_images.pop(0)
    indeces = list(indeces)
    canvas_index = indeces.pop(0)
    return [image, [np.delete(colors,0,axis=0),bin_images,indeces], [canvas_color,bin_image, canvas_index]]

def decompose(image,input_pallete,n_colors=0,canvas_color = None):
    if input_pallete is None:
        pallete = []
    else:
        pallete = deepcopy(input_pallete)
        
    original_n_colors = n_colors

    if not (canvas_color is None):
        if len(pallete)>0:
            pallete.append(canvas_color)
        n_colors+=1


    if(original_n_colors>0):
        print "CLASSIFY: KMEANS"
        image,bin_images,colors = decompose_kMeans(image,n_colors)
        if len(pallete) == 0:
            indeces = range(len(colors))
        else:
            print "... mapping k-means to pallete"
            colors , indeces = mapColors(colors, pallete)
            for i in range(len(colors)):
                pts = np.where(bin_images[i]==0)
                image[pts[0],pts[1],:]=colors[i]
        img_list = []
        for i in range(len(indeces)):
            img_list.append((indeces[i],bin_images[i],colors[i]))

        # print "Img List", img_list 
        img_list.sort()
        bin_images=[]
        colors=[]
        indeces=[]
        for t in img_list:
            indeces.append(t[0])
            bin_images.append(t[1])
            colors.append(t[2])
    else:
        print "CLASSIFY: SIMPLE"
        image,bin_images,colors,indeces = decompose_simple(image,pallete)

        temp_colors = []
        for c in colors:
            temp_colors.append(c)

        colors = temp_colors

    if not (canvas_color is None):
        if len(pallete)>0:
            if(len(pallete)-1) in indeces:
                canvas_index = indeces.index(len(pallete)-1);
        else:
            _,idx = mapColors([canvas_color],colors)
            canvas_index = idx[0]
        bin_images.pop(canvas_index)
        colors.pop(canvas_index)
        indeces.pop(canvas_index)


    return image , bin_images, np.array(colors).astype('uint8').tolist() , indeces

def color_quantize(image, n_colors=2, size_to=500):
    if size_to>0:
        small_img = util.resize(image,size_to)
    else:
        raise ValueError

    pixel = np.reshape(small_img,(small_img.shape[0]*small_img.shape[1],3))

    # performing the clustering
    centroids,_ = kmeans(np.float32(pixel),n_colors,iter=300)

    return np.uint8(centroids)

def decompose_simple(image, colors):
    # colors_lab = []
    # for color in colors:
    #     color_lab = rgb2lab(color)
    #     # colors_lab.append(color_lab)
    #     colors_lab.append([color_lab.lab_l,color_lab.lab_a,color_lab.lab_b])

    image_lab = image.astype('float32') * 1./255
    image_lab = cv2.cvtColor(image_lab,cv2.COLOR_BGR2LAB)

    colors_lab = np.array(colors).astype('float32') * 1./255
    colors_lab = cv2.cvtColor(np.array([colors_lab]),cv2.COLOR_BGR2LAB)[0]

    pixel = np.reshape(image_lab,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors_lab)

    # qnt=[]
    # for p in pixel:
    #     p_lab = rgb2lab(p)
    #     min_error =999999
    #     min_index = -1
    #     c_index=0
    #     for c_lab in colors_lab:
    #         err = delta_e_cie2000(p_lab, c_lab)
    #         if(err<min_error):
    #             min_error=err
    #             min_index = c_index
    #         c_index+=1
    #     qnt.append(min_index);
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))

    colors=np.array(colors)
    image = colors[centers_idx]
    image = np.uint8(image)

    bin_images = [] # The 1-color images.

    for index in range(0, len(colors)):
        # Create empty image
        bin_image = 255-np.zeros((image.shape[0],image.shape[1],1), np.uint8)
        bin_image[np.where((centers_idx == index))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.

    return image , bin_images , colors, range(len(colors))

def decompose_kMeans(image, n_colors):
    colors = color_quantize(image,n_colors)

    pixel = np.reshape(image,(image.shape[0]*image.shape[1],3))
    qnt,_ = vq(pixel,colors)
    centers_idx = np.reshape(qnt,(image.shape[0],image.shape[1]))

    image = colors[centers_idx]
    image = np.uint8(image)

    bin_images = [] # The 1-color images.

    for index in range(0, len(colors)):
        # Create empty image
        bin_image = 255-np.zeros((image.shape[0],image.shape[1],1), np.uint8)
        bin_image[np.where((centers_idx == index))] = [0]
        bin_images.append(bin_image) # Add to the list of color specific images.

    return image , bin_images , colors

def rgb2lab ( inputColor ) :
    color_rgb = sRGBColor(inputColor[2], inputColor[1], inputColor[0])
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

# def find_max_error(img_colors, paint_colors):
#     max_error = 0
#     for index in range(len(img_colors)):
#         delta_e = delta_e_cie2000(img_colors[index], paint_colors[index])
#         if delta_e > max_error:
#             max_error = delta_e

#     return max_error

# def find_avg_error(img_colors, paint_colors):
#     avg = 0
#     for index in range(len(img_colors)):
#         delta_e = delta_e_cie2000(img_colors[index], paint_colors[index])
#         avg += float(delta_e)/len(img_colors)

#     return avg

def find_error(img_colors, paint_colors):
    max_error = 0
    avg = 0
    for index in range(len(img_colors)):
        delta_e = delta_e_cie2000(img_colors[index], paint_colors[index])
        # print delta_e
        avg += float(delta_e)/len(img_colors)
        if delta_e > max_error:
            max_error = delta_e

    return avg

def mapColors(img_colors, paint_colors):
    '''Return an array of img_colors containing only colors within paint colors. 
    Also returns an array conatining the ideces in paint_colors from which new colors were found'''

    colors_lab, pallete_lab = convert(img_colors, paint_colors)

    # Get the number of paint colors and kmeans colors
    num_colors_pallete = len(paint_colors) # N 
    num_colors_kmeans = len(img_colors) # R

    min_uses = (num_colors_kmeans)/(num_colors_pallete)
    color_options = []
    for i in range(min_uses):
        color_options.extend(range(num_colors_pallete))

    # Get all possible combinations
    sorted_combinations = combinations(range(num_colors_pallete), num_colors_kmeans%num_colors_pallete)

    unique_permutations = set()
    
    for combo in sorted_combinations:
        combo = list(combo)
        combo.extend(color_options)
        for p in permutations(combo):
            unique_permutations.add(p)

    unique_permutations = list(unique_permutations)

    pallete_lab = np.array(pallete_lab)
    min_error = find_error(colors_lab, pallete_lab[np.array(unique_permutations[0])])
    min_combo = unique_permutations[0]
    for combo in unique_permutations:
        # print "paint combo", temp_paint_combo
        err = find_error(colors_lab , pallete_lab[np.array(combo)])
        if err < min_error:
            min_error = err
            min_combo= combo

    paint_colors = np.array(paint_colors)
    colors = paint_colors[np.array(min_combo)]

    return np.array(colors), np.array(min_combo)

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

    return img_colors, best_index