import numpy as np

class Eole:
    def __init__(self, direction, speed):
        self.wind = np.array([direction, speed], dtype="float")

    def get_wind_at(self, pos):
        return self.wind
