import numpy as np

class Puff():
    def __init__(self, pos, width, height, orientation, speed, direction):
        self.pos = pos
        self.width = width
        self.height = height
        self.orientation = orientation
        self.speed = speed
        self.direction = direction

class Eole:
    def __init__(self, direction, speed, width, height, step):
        self.wind = np.array([direction, speed], dtype="float")

        self.width = width
        self.height = height
        self.step = step

        self.puffs = []
        self.puff_direction_grid = np.zeros((int(height/step), int(width/step)), dtype="float")
        self.puff_speed_grid = np.zeros((int(height/step), int(width/step)), dtype="float")

        self.create_puff()
        self.create_puff()

    def get_wind_at(self, pos):
        x = int(pos[0] / self.step) - 1
        y = int(pos[1] / self.step) - 1
        puff_dir = self.puff_direction_grid[x, y]
        puff_speed = self.puff_speed_grid[x, y]
        return self.wind + np.array([puff_dir, puff_speed])

    def get_direction_grid(self):
        return self.wind[0] + self.puff_direction_grid

    def get_speed_grid(self):
        return self.wind[1] + self.puff_speed_grid

    def update(self, dt):
        self.move_puff(dt)

    def move_puff(self, dt):
        self.puff_direction_grid = np.zeros((int(self.height/self.step), int(self.width/self.step)), dtype="float")
        self.puff_speed_grid = np.zeros((int(self.height/self.step), int(self.width/self.step)), dtype="float")

        for puff in self.puffs:
            puff.pos -= np.array([np.cos(puff.direction + self.wind[0]), np.sin(puff.direction + self.wind[0])]) * self.wind[1] * dt

            # 1/3 full, rest prop

            for i in range(int(self.height/self.step)):
                x = int((i+0.5) * self.step)

                for j in range(int(self.width/self.step)):
                    y = int((j+0.5) * self.step)

                    x_coef = 0
                    x_diff = abs(x - puff.pos[0])
                    if x_diff < puff.height / 6:
                        x_coef = 1
                    elif x_diff < puff.height / 2:
                        x_coef = (x_diff - puff.height / 2) / (puff.height / 6 - puff.height / 2)

                    y_coef = 0
                    y_diff = abs(y - puff.pos[1])
                    if y_diff < puff.width / 6:
                        y_coef = 1
                    elif y_diff < puff.width / 2:
                        y_coef = (y_diff - puff.width / 2) / (puff.width / 6 - puff.width / 2)

                    coef = x_coef * y_coef

                    dir = puff.direction * coef
                    speed = puff.speed * coef
                    if self.puff_speed_grid[i, j] + speed != 0:
                        self.puff_direction_grid[i, j] = (self.puff_direction_grid[i, j] * self.puff_speed_grid[i, j] + dir * speed) / (self.puff_speed_grid[i, j] + speed)
                    self.puff_speed_grid[i, j] += speed

            if puff.pos[0] < -self.height / 2:
                self.puffs.remove(puff)
                self.create_puff()

    def create_puff(self):
        width = np.random.randint(300, 600)
        height = np.random.randint(300, 600)
        pos = np.array([self.height, self.width], dtype="float") / 2 \
            + np.array([np.cos(self.wind[0]), np.sin(self.wind[0])]) * max(self.height, self.width)/2 \
            + np.array([np.random.randint(-self.height/2, self.height/2), np.random.randint(-self.width/2, self.width/2)])
        orientation = np.radians(np.random.randint(0, 90))
        speed = np.random.randint(20, 80)/10.
        direction = np.radians(np.random.randint(-20, 20))

        self.puffs.append(Puff(pos, width, height, orientation, speed, direction))
