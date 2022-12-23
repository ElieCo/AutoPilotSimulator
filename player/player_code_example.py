import sys
import numpy as np

sys.path.append("..")
from src.boat import AutoPilot, NoobPilot

class PlayerPilot(AutoPilot):
    update = NoobPilot.update

    def __init__(self):
        super(PlayerPilot, self).__init__()
        self.yaw_setpoint = None
        self.up_wind_angle = np.radians(40)
