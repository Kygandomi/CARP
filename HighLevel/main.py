from recomposition.skeleton.skeletonRecompose import *
from recomposition.skeleton.medialAxisRecompose import *
from recomposition.skeleton.iterativeSkeletonRecompose import *
from recomposition.medialAxis.iterativeBlendedRecompose import *
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.erosion.erosionRecompose import *
from recomposition.blendedRecompose import *
from common.util import *
from common import color_pallete
from decomposition.decomp_color.decomp_color import *
import cv2

# color1 = np.array(color_pallete.colorMap["green"])
# color_rgb1 = sRGBColor(color1[2], color1[1], color1[0])
# color_lab1 = convert_color(color_rgb1, LabColor)

# color2 = [54,191,127]
# color_rgb2 = sRGBColor(color2[2], color2[1], color2[0])
# color_lab2 = convert_color(color_rgb2, LabColor)
# err = delta_e_cie1994(color_lab1, color_lab2)

# print "err: ", err, " | ",color1, " - ", color2

desiredImg = readImage("cobblestone.png")

pallete = []
canvas_color = None
n_colors = 4

canvas_color = [255,255,255]
# pallete = [[0,0,0], [0,255,255], [255,255,255], [0,0,255]]
# pallete = color_pallete.build("black red yellow")
segmented_image, color_segments, colors, indeces = decompose(desiredImg, pallete,n_colors,canvas_color)

display(desiredImg,"desired")
display(segmented_image,"segmented")

print "Pallete: ", pallete
print "Kmeans: ", colors
print "resulting indeces", indeces

# recomposer = skeletonRecomposer(binImg, [2])
# recomposer = iterativeErosionRecomposer(binImg, [2])
# recomposer = erosionRecomposer(binImg, [2])

out=255*np.ones(segmented_image.shape,dtype='uint8')
for i in range(len(color_segments)):
    binImg = color_segments[i]
    # binImg = 255*np.ones(binImg.shape, dtype='uint8')

    recomposer = iterativeBlendedRecomposer(binImg, [4])

    LLT = recomposer.recompose()

    #LLT = mapLLT(LLT,binImg.shape)

    # display(testLLT(LLT,scale=3,thickness=2))
    print "color: ",colors[i]
    out = drawLLT(LLT,out,thickness=3,color = colors[i])
display(out)

print "Done"