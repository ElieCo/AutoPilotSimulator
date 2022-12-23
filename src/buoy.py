import numpy as np

class Buoy:
    def __init__(self, x, y, valid_dist):
        self.pos = np.array([float(x), float(y)])
        self.valid_dist = valid_dist
