# colorMap = {
#     "blue" : [255,0,0],
#     "green" : [0,255,0],
#     "red" : [0,0,255],
#     "yellow" : [0,255,255],
#     "purple" : [255,0,255],
#     "cyan" : [255,255,0],
#     "orange" : [0,127,255],
#     "pink" : [127,0,255],
#     "lime" : [127,255,0],
#     "azure" : [255,127,0],
#     "white" : [255,255,255],
#     "light_gray" : [64,64,64],
#     "gray" : [127,127,127],
#     "dark_gray" : [191,191,191],
#     "black" : [0,0,0]
# }

# B G R is lyfe
colorMap = {
    "blue" : [255,0,0],
    "green" : [0,255,0],
    "yellow" : [15,152,146],
    "red" : [9,0,87],
    "white" : [170,170,170],
    "black" : [0,0,0],
    "black_measured" : [10,10,10],
    "custom_yellow" : [65, 138, 156],
    "ligher_gray" : [65, 76, 77],
    "light_gray" : [29, 37, 34]
}

def all():
    palette = []
    for color in colorMap:
        palette.append(colorMap[color])
    return palette

def build(color_string):
    """
    Builds a pallete of colors based on colors specified in the color string.
    :return: [[c1,c2,c3],[c4,c5,c6], ...]
    """
    palette = []
    color_string = color_string.split(" ")
    color_string = [x for x in color_string if "" != x]
    for color in color_string:
        color = color.lower()
        try:
            palette.append(colorMap[color])
        except KeyError:
            print "Unable to read color: {}. Did you misspell a color in your pallete string?".format(color)
            raise

    return palette