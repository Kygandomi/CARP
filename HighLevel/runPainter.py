
from paint_with_pmd.painter_bot import *
from common import color_pallete
from common.util import *

bot = painter_bot()

bot.connect_camera([1])

bot.selectImage("boat2.png", "resources/images/input/")

n_colors = 3
canvas_color = None 
pallete = []

canvas_color = color_pallete.colorMap["white"]
# pallete = [[190,202,203], [127,148,158],[75,95,108],[29,36,42]] #doggo pallete
pallete = color_pallete.build("red yellow black")
# pallete = color_pallete.build("black_measured")

display(bot.desiredImg)
print "DECOMPOSE"
bot.decompose(n_colors,pallete,canvas_color)
display(bot.segmentedImg)
print "RECOMPOSE"
bot.recompose([4])
display(bot.lltImg)

bot.connect_eth(ip = '192.168.178.7',port = 1234)
bot.paint()
# bot.paint_with_feedback([4])