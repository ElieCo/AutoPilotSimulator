import numpy as np
import copy

# Speed table
S_TABLE = [
    0.0,
    0.04347826086956522,
    0.2173913043478261,
    0.47826086956521746,
    0.5652173913043479,
    0.673913043478261,
    0.8478260869565218,
    0.8913043478260869,
    0.9347826086956522,
    0.9782608695652175,
    1.0,
    0.9782608695652175,
    0.9782608695652175,
    0.8913043478260869,
    0.8260869565217391,
    0.6956521739130436,
    0.6521739130434783,
    0.5869565217391305,
    0.5434782608695653
]

# 1/TACK_CHANCE is the probability that a Nooboat do a tack
TACK_CHANCE = 1000

# Calculate the bearing between the positions "from" an "to"
def bearing(from_, to):
    dx = to[0] - from_[0]
    dy = to[1] - from_[1]
    return np.arctan2(dy, dx)

# Find the angle + k.2.PI closest to the target (usefull to compare to angles)
def get_angle_around(angle, target):
    while angle < target - np.pi:
        angle += 2 * np.pi
    while angle > target + np.pi:
        angle -= 2 * np.pi
    return angle

# Mother class of every Pilot
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


    # Function called to update the decisions of the pilot
    def update(self):
        raise("The update function of the AutoPilot class need to be overwritten !")

# Example of a noob pilot
class NoobPilot(AutoPilot):
    def __init__(self):
        super(NoobPilot, self).__init__()
        self.yaw_setpoint = None # Yaw target
        self.up_wind_angle = np.radians(30) # Angle min between the boat and the wind

    def update(self):
        # Wait that the previous yaw target have been reached to decide of an other one
        if self.yaw_setpoint is None or abs(self.yaw_setpoint - self.obs["yaw"]) < np.radians(5):

            # Set the bearinf to the next buoy as the yaw setpoint
            self.yaw_setpoint = get_angle_around(self.obs["buoy_bearing"], self.obs["yaw"])

            # Prepare the wind angle to be able to compare it to the yaw
            wind = get_angle_around(self.obs["wind_direction"], self.obs["yaw"])
            # Get the angle between the wind and the desired yaw in [-PI;PI]
            wind_dest = get_angle_around(wind - self.yaw_setpoint, 0)
            # If this angle is smaller than the up_wind_angle, change the yaw setpoint
            if abs(wind_dest) < self.up_wind_angle:
                # Get an hazard coef equals to 1 or -1
                hazard_coef = 1 if np.random.randint(TACK_CHANCE) != 0 else -1
                # Choose the closest leg to the actual yaw and use the hazard coef to do a tack sometimes
                if abs(wind - self.up_wind_angle - self.obs["yaw"]) > abs(wind + self.up_wind_angle - self.obs["yaw"]):
                    self.yaw_setpoint = wind + self.up_wind_angle * hazard_coef
                else:
                    self.yaw_setpoint = wind - self.up_wind_angle * hazard_coef

        # Decide of the helm angle depending of the diff between the yaw and the setpoint
        if abs(self.yaw_setpoint - self.obs["yaw"]) < np.radians(2):
            self.cmd["helm_angle"] = 0
        elif self.yaw_setpoint > self.obs["yaw"]:
            self.cmd["helm_angle"] = np.radians(20)
        else:
            self.cmd["helm_angle"] = np.radians(-20)

# A Noob a little less bad than the other ones
class ChampiNoobPilot(NoobPilot):
    def __init__(self):
        super(ChampiNoobPilot, self).__init__()
        self.up_wind_angle = np.radians(40)

class Boat:
    def __init__(self, pilot, name, start_pos):
        self.pilot = pilot

        self.reset(start_pos)

        self.name = name

        self.wind = [0, 0]

    def reset(self, pos):
        self.pos = pos.copy()
        self.speed = 0
        self.yaw = 0
        self.roll = 0

        self.helm_angle = 0

        self.buoy_index = 0
        self.all_buoys_reached = False


    def get_local_wind_angle(self):
        return get_angle_around(self.wind[0] - self.yaw, 0)

    def move(self, dt):
        # Update speed
        wind_deg = np.degrees(self.get_local_wind_angle())
        i = abs(wind_deg) / 10
        i0 = int(round(i))
        coef = 0
        if i0 >= len(S_TABLE) - 1:
            coef = S_TABLE[-1]
        else:
            k = (i - i0)
            coef = S_TABLE[i0] + (S_TABLE[i0 + 1] - S_TABLE[i0]) * k
        self.speed = coef * self.wind[1]

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

        if len(buoy_data) and self.buoy_index >= len(buoy_data):
            self.buoy_index = 0
            self.all_buoys_reached = True

    def update(self, wind_data, buoy_data, boats):
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
