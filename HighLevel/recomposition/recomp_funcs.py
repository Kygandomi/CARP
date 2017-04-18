from medialAxis.iterativeBlendedRecompose import *
from medialAxis.medialAxisRecompose import *
from iterativeErosion.iterativeErosionRecompose import *
# from fill.linearFillRecompose import *

def iterativeBlendedRecomp(img,args):
	recomposer = iterativeBlendedRecomposer(img,args)
	return recomposer.recompose()

def medialAxisRecomp(img,args):
	recomposer = medialAxisRecomposer(img,args)
	return recomposer.recompose()

def iterativeErosionRecomp(img,args):
	recomposer = iterativeErosionRecomposer(img,args)
	return recomposer.recompose()
