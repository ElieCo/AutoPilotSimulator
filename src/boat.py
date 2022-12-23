import numpy as np
import copy

S_TABLE = [0, 0.2, 1, 2.2, 2.6, 3.1, 3.9, 4.1, 4.3, 4.5, 4.6, 4.5, 4.5, 4.1, 3.8, 3.2, 3, 2.7, 2.5]
TACK_CHANCE = 1000

def bearing(from_, to):
    dx = to[0] - from_[0]
    dy = to[1] - from_[1]
    return np.arctan2(dy, dx)

def get_angle_around(angle, target):
    while angle < target - np.pi:
        angle += 2 * np.pi
    while angle > target + np.pi:
        angle -= 2 * np.pi
    return angle

class AutoPilot:
    def __init__(self):
        # Init all the observations the pilot can have
        self.obs = {
            "pos": np.array([0.0, 0.0]),
            "yaw": 0,
            "pitch": 0,
            "roll": 0,

            "wind_speed": 0,
            "wind_direction": 0,

            "buoy_bearing": 0,
            "buoy_distance": 0,

            "boats": [] # List of {"bearing": 0, "distance": 0, "speed": 0, "yaw": 0, "roll": 0}
        }

        # Init all cmd
        self.cmd = {
            "helm_angle": 0
        }


    def update(self):
        raise("The update function of the AutoPilot class need to be overwritten !")

class NoobPilot(AutoPilot):
    def __init__(self):
        super(NoobPilot, self).__init__()
        self.yaw_setpoint = None
        self.up_wind_angle = np.radians(30)

    def update(self):
        if self.yaw_setpoint is None or abs(self.yaw_setpoint - self.obs["yaw"]) < np.radians(5):

            self.yaw_setpoint = get_angle_around(self.obs["buoy_bearing"], self.obs["yaw"])

            wind = get_angle_around(self.obs["wind_direction"], self.obs["yaw"])
            wind_dest = get_angle_around(wind - self.yaw_setpoint, 0)
            if abs(wind_dest) < self.up_wind_angle:
                hazard_coef = 1 if np.random.randint(TACK_CHANCE) != 0 else -1
                if abs(wind - self.up_wind_angle - self.obs["yaw"]) > abs(wind + self.up_wind_angle - self.obs["yaw"]):
                    self.yaw_setpoint = wind + self.up_wind_angle * hazard_coef
                else:
                    self.yaw_setpoint = wind - self.up_wind_angle * hazard_coef


        if abs(self.yaw_setpoint - self.obs["yaw"]) < np.radians(2):
            self.cmd["helm_angle"] = 0
        elif self.yaw_setpoint > self.obs["yaw"]:
            self.cmd["helm_angle"] = np.radians(20)
        else:
            self.cmd["helm_angle"] = np.radians(-20)

class ChampiNoobPilot(NoobPilot):
    def __init__(self):
        super(ChampiNoobPilot, self).__init__()
        self.up_wind_angle = np.radians(40)

class Boat:
    def __init__(self, pilot, name):
        self.pilot = pilot

        self.pos = np.array([0.0, 0.0])
        self.speed = 10
        self.yaw = 0
        self.roll = 0

        self.helm_angle = 0

        self.name = name

        self.buoy_index = 0

        self.wind = [0, 0]

    def get_local_wind_angle(self):
        return get_angle_around(self.wind[0] - self.yaw, 0)

    def move(self, dt):
        # Update speed
        wind_deg = np.degrees(self.get_local_wind_angle())
        i = abs(wind_deg) / 10
        i0 = int(round(i))
        if i0 >= len(S_TABLE) - 1:
            self.speed = S_TABLE[-1]
        else:
            k = (i - i0)
            self.speed = S_TABLE[i0] + (S_TABLE[i0 + 1] - S_TABLE[i0]) * k

        # Update yaw
        dy = self.helm_angle * dt * 0.5
        self.yaw += dy

        # Update position
        dd = dt * self.speed
        dp = np.array([np.cos(self.yaw), np.sin(self.yaw)]) * dd
        self.pos += dp

    def validate_buoy(self, buoy_data):
        if self.buoy_index < len(buoy_data):
            if np.linalg.norm(buoy_data[self.buoy_index].pos - self.pos) < buoy_data[self.buoy_index].valid_dist:
                self.buoy_index += 1

        if len(buoy_data):
            self.buoy_index = self.buoy_index % len(buoy_data)

    def updatePilot(self, wind_data, buoy_data, boats):
        self.validate_buoy(buoy_data)

        # From x,y buoy position to observations
        self.pilot.obs["buoy_bearing"] = bearing(self.pos, buoy_data[self.buoy_index].pos)
        self.pilot.obs["buoy_distance"] = np.linalg.norm(buoy_data[self.buoy_index].pos - self.pos)

        # From own data to pilot observations
        self.pilot.obs["pos"] = self.pos.copy()
        self.pilot.obs["speed"] = self.speed
        self.pilot.obs["yaw"] = self.yaw

        # From boats data to pilot observations
        self.pilot.obs["boats"] = []
        for boat in boats:
            if boat != self:
                boat_obs = {
                    "bearing": bearing(self.pos, boat.pos),
                    "distance": np.linalg.norm(boat.pos - self.pos),
                    "speed": boat.speed,
                    "yaw": boat.yaw,
                    "roll": boat.roll
                }
                self.pilot.obs["boats"].append(copy.deepcopy(boat_obs))


        # Save wind for Boat matters
        self.wind = wind_data

        # From wind data to pilot observations
        self.pilot.obs["wind_direction"] = wind_data[0]
        self.pilot.obs["wind_speed"] = wind_data[1]

        self.pilot.update()

        self.helm_angle = self.pilot.cmd["helm_angle"]
