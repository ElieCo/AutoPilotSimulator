import numpy as np

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
        self.helm_angle = 0

    def update(self, own_data, wind_data, next_buoy, boats_data):
        raise("The update function of the AutoPilot need to be overwritten !")

class NoobPilot(AutoPilot):
    def __init__(self):
        super(NoobPilot, self).__init__()
        self.yaw_setpoint = None

    def update(self, own_data, wind_data, next_buoy, boats_data):
        if self.yaw_setpoint is None or abs(self.yaw_setpoint - own_data["yaw"]) < np.radians(5):

            self.yaw_setpoint = get_angle_around(bearing(own_data["pos"], next_buoy.pos), own_data["yaw"])

            wind = get_angle_around(wind_data[0], own_data["yaw"])
            wind_dest = get_angle_around(wind - self.yaw_setpoint, 0)
            if abs(wind_dest) < np.radians(30):
                hazard_coef = 1 if np.random.randint(TACK_CHANCE) != 0 else -1
                if abs(wind - np.radians(30) - own_data["yaw"]) > abs(wind + np.radians(30) - own_data["yaw"]):
                    self.yaw_setpoint = wind + np.radians(30) * hazard_coef
                else:
                    self.yaw_setpoint = wind - np.radians(30) * hazard_coef


        if abs(self.yaw_setpoint - own_data["yaw"]) < np.radians(2):
            self.helm_angle = 0
        elif self.yaw_setpoint > own_data["yaw"]:
            self.helm_angle = np.radians(20)
        else:
            self.helm_angle = np.radians(-20)


class Boat:
    def __init__(self, pilot, name):
        self.pilot = pilot
        self.pos = np.array([0.0, 0.0])
        self.speed = 10
        self.yaw = 0
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

    def updatePilot(self, wind_data, buoy_data, boats_data):
        self.validate_buoy(buoy_data)

        self.wind = wind_data

        own_data = {"pos": self.pos.copy(), "speed": self.speed, "yaw": self.yaw}
        self.pilot.update(own_data, wind_data, buoy_data[self.buoy_index], boats_data)

        self.helm_angle = self.pilot.helm_angle
