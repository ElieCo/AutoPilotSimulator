import numpy as np

class AutoPilot:
    def __init__(self):
        pass

class NoobPilot(AutoPilot):
    def __init__(self):
        super(NoobPilot, self).__init__()

class Boat:
    def __init__(self, pilot, name):
        self.pilot = pilot
        self.pos = np.array([0.0, 0.0])
        self.speed = 0
        self.yaw = 0
        self.helm_angle = 0
        self.name = name

    def move(self, dt):
        pass

    def updatePilot(self):
        self.pilot.update()
