
from paint_with_pmd.painter_bot import *
from common import color_pallete
from common.util import *

bot = painter_bot()

if not bot.connect_camera([1]):
	raise Exception('Could not connect to Camera')
	pass

bot.selectImage("turtle2.png", "resources/images/input/")

n_colors = 3
canvas_color = None 
pallete = []

canvas_color = color_pallete.colorMap["white"]
# pallete = [[190,202,203], [127,148,158],[75,95,108],[29,36,42]] #doggo pallete
# pallete = [[124,74,17], [7,84,220], [5,10,5]] # fish
# pallete = color_pallete.build("red yellow black") #boat pallete
# pallete = [[240,235,240], [50,77,127],[50,57,108],[21,60,106],[10,10,51]] #fox pallete
pallete = [[125,174,156], [68,118,77], [33,47,34]] # turtle

# pallete = color_pallete.build("black_measured")
# pallete=[]

display(bot.desiredImg,"desired")
print "DECOMPOSE"
bot.decompose(n_colors,pallete,canvas_color)
display(bot.segmentedImg,"segmented")
print "RECOMPOSE"
bot.recompose([3])
display(bot.lltImg,"LLT simulation")

bot.connect_eth(ip = '192.168.178.7',port = 1234)
bot.paint()
bot.paint_with_feedback([4])