
from paint_with_pmd.painter_bot import *
from common import color_pallete
from common.util import *

bot = painter_bot()

if not bot.connect_camera([1]):
	raise Exception('Could not connect to Camera')
	pass

bot.selectImage("bluejay.png", "resources/images/input/")

n_colors = 4
canvas_color = None 
pallete = []

canvas_color = color_pallete.colorMap["white"]
# pallete = [[190,202,203], [127,148,158],[75,95,108],[29,36,42]] #doggo pallete
# pallete = [[124,74,17], [7,84,220], [5,10,5]] # fish
# pallete = color_pallete.build("red yellow black") #boat pallete
# pallete = [[240,235,240], [50,77,127],[50,57,108],[21,60,106],[10,10,51]] #fox pallete
# pallete = [[125,174,156], [68,118,77], [33,47,34]] # turtle
# pallete = [[113,121,180], [80,92,148], [64,75,117], [31,37,48], [215, 198,198]] # gennert
# pallete = [[161,168,207], [74,93,197], [42,45,172], [19,10,128], [21, 93, 83]] # apple
# pallete = [[158,171,181], [116,129,143], [82,93,105], [44,51,58]] # kitten
# pallete = [[64,220,245], [12,178,211], [132,136,135], [30,30,30]] # car
pallete = [[224,189,181], [197,134,113], [151,82,47], [30,30,30]] # bluejay


# pallete = color_pallete.build("black_measured")

display(bot.desiredImg,"desired")
print "DECOMPOSE"
bot.decompose(n_colors,pallete,canvas_color)
display(bot.segmentedImg,"segmented")
print "RECOMPOSE"
bot.recompose([3], False)
display(bot.lltImg,"LLT simulation")

bot.connect_eth(ip = '192.168.178.7',port = 1234)
bot.paint()
bot.paint_with_feedback([4])