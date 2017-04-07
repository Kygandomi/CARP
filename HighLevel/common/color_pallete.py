# colorMap = {
#     "blue" : [255,0,0],
#     "green" : [0,255,0],
#     "yellow" : [0,255,255],
#     "red" : [0,25,255],
#     "white" : [255,255,255],
#     "black" : [0,0,0]
# }

colorMap = {
    "blue" : [255,0,0],
    "green" : [0,255,0],
    "yellow" : [15,152,146],
    "red" : [9,0,87],
    "white" : [255,255,255],
    "black" : [0,0,0]
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