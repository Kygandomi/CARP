blue = [255,0,0]
green = [0,255,0]
yellow = [0,233,255]
red = [0,0,255]
white = [255,255,255]
black = [0,0,0]

flask_green = [49, 190, 124]
flask_blue = [167, 86, 17]

colorMap = {
    "blue" : [255,0,0],
    "green" : [0,255,0],
    "yellow" : [0,233,255],
    "red" : [0,0,255],
    "white" : [255,255,255],
    "black" : [0,0,0]
}


def buildPallete(color_string):
    """
    Builds a pallete of colors based on colors specified in the color string.
    :return: [[c1,c2,c3],[c4,c5,c6], ...]
    """
    palette = []
    color_string = color_string.split(" ")
    color_string = [x for x in color_string if "" != x]
    print color_string
    for color in color_string:
        color = color.lower()
        try:
            palette.append(colorMap[color])
        except KeyError:
            print "Unable to read color: {}. Did you misspell a color in your pallete string?".format(color)
            raise

    return palette