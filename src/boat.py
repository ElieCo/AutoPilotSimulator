import numpy as np

class AutoPilot:
    def __init__(self):
        self.helm_angle = 0

    def update(self):
        raise("The update function of the AutoPilot need to be overwritten !")

class NoobPilot(AutoPilot):
    def __init__(self):
        super(NoobPilot, self).__init__()

class Boat:
    def __init__(self, pilot, name):
        self.pilot = pilot
        self.pos = np.array([0.0, 0.0])
        self.speed = 10
        self.yaw = 0
        self.helm_angle = np.radians(10)
        self.name = name

    def move(self, dt):
        dy = self.helm_angle * dt * 0.5
        self.yaw += dy

        dd = dt * self.speed
        dp = np.array([np.cos(self.yaw), np.sin(self.yaw)]) * dd
        self.pos += dp

    def updatePilot(self):
        self.pilot.update()

        self.helm_angle = self.pilot.helm_angle
