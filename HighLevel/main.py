from recomposition.skeleton.skeletonRecompose import *
from recomposition.skeleton.medialAxisRecompose import *
from recomposition.skeleton.iterativeSkeletonRecompose import *
from recomposition.iterativeErosion.iterativeErosionRecompose import *
from recomposition.erosion.erosionRecompose import *
from recomposition.blendedRecompose import *
from common.util import *
from common import color_pallete
from decomposition.decomp_color.decomp_color import *
import cv2

desiredImg = readImage("boat2.png")

segmented_image, [colors,color_segments], [canvas,canvas_segment]  = decompose(desiredImg, 4, [], color_pallete.colorMap["white"])

# recomposer = skeletonRecomposer(binImg, [2])
# recomposer = iterativeErosionRecomposer(binImg, [2])
# recomposer = erosionRecomposer(binImg, [2])


out=255*np.ones(segmented_image.shape,dtype='uint8')
for i in range(len(color_segments)):
    binImg = color_segments[i]
    binImg = 255*np.ones(binImg.shape, dtype='uint8')

    recomposer = blendedRecomposer(binImg, [2])

    LLT = recomposer.recompose()

    #LLT = mapLLT(LLT,binImg.shape)

    # display(testLLT(LLT,scale=3,thickness=2))
    out = drawLLT(LLT,out,thickness=3,color = colors[i])
display(out)

print "Done"