class recomposer(object):
    def __init__(self, image, args):
        self.decompImage = image
        self.args = args
        pass
    def recompose(self):
        raise NotImplementedError("You need to implement a recomposer!")