from tkinter import *
from threading import Thread
import numpy as np
import time

def simu_to_tk_coords(x, y, width, height):
    return y, height - x

class ArrowDraw():
    def __init__(self, canvas, canvas_width, canvas_height, x, y, dir, speed, color="black"):
        self.canvas = canvas
        self.color = color

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.x = x
        self.y = y
        self.direction = dir
        self.speed = speed

        self.poly = self.canvas.create_polygon(0, 0, fill="", outline=color, width=3)
        self.redraw(dir, speed)

    def redraw(self, direction, speed):
        self.direction = direction
        self.speed = speed

        if self.canvas is not None:
            l = speed * 2

            x_butt = self.x + np.cos(direction) * l / 2
            y_butt = self.y + np.sin(direction) * l / 2

            x_head = self.x - np.cos(direction) * l / 2
            y_head = self.y - np.sin(direction) * l / 2

            x_right = x_head + np.cos(direction + np.pi/4) * l / 8
            y_right = y_head + np.sin(direction + np.pi/4) * l / 8

            x_left = x_head + np.cos(direction - np.pi/4) * l / 8
            y_left = y_head + np.sin(direction - np.pi/4) * l / 8

            x_butt, y_butt = simu_to_tk_coords(x_butt, y_butt, self.canvas_width, self.canvas_height)
            x_head, y_head = simu_to_tk_coords(x_head, y_head, self.canvas_width, self.canvas_height)
            x_right, y_right = simu_to_tk_coords(x_right, y_right, self.canvas_width, self.canvas_height)
            x_left, y_left = simu_to_tk_coords(x_left, y_left, self.canvas_width, self.canvas_height)

            self.canvas.coords(self.poly, x_butt, y_butt, x_head, y_head, x_right, y_right, x_head, y_head, x_left, y_left, x_head, y_head)


class BoatDraw:
    def __init__(self, canvas, x, y, yaw, helm_angle, canvas_width, canvas_height, color="black"):
        self.canvas = canvas
        self.color = color

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.poly = self.canvas.create_polygon(0, 0, fill=color, outline=color, width=3)
        self.redraw(x, y, yaw, helm_angle)

    def redraw(self, x, y, yaw, helm_angle):
        if self.canvas is not None:
            self.canvas.coords(self.poly, *self.getPolygonCoords(x, y, yaw, helm_angle))

    def getPolygonCoords(self, x, y, yaw, helm_angle):

        l1 = 20
        x1 = x + np.cos(yaw) * l1
        y1 = y + np.sin(yaw) * l1

        l23 = 4
        x2 = x + np.cos(yaw + np.pi/2) * l23
        y2 = y + np.sin(yaw + np.pi/2) * l23
        x3 = x + np.cos(yaw - np.pi/2) * l23
        y3 = y + np.sin(yaw - np.pi/2) * l23

        lh = 4
        xh = x - np.cos(yaw + helm_angle) * lh
        yh = y - np.sin(yaw + helm_angle) * lh

        x, y = simu_to_tk_coords(x, y, self.canvas_width, self.canvas_height)
        x1, y1 = simu_to_tk_coords(x1, y1, self.canvas_width, self.canvas_height)
        x2, y2 = simu_to_tk_coords(x2, y2, self.canvas_width, self.canvas_height)
        x3, y3 = simu_to_tk_coords(x3, y3, self.canvas_width, self.canvas_height)
        xh, yh = simu_to_tk_coords(xh, yh, self.canvas_width, self.canvas_height)

        return xh, yh, x, y, x2, y2, x1, y1, x3, y3, x, y


class Displayer(Thread):
    def __init__(self, display_dt_s, buoys, width, height, fake_window=False):
        Thread.__init__(self)

        self.window = None
        self.canvas = None

        self.width = width
        self.height = height

        self.dt = display_dt_s
        self.ts = None
        self.boats = {}
        self.buoys = buoys

        self.arrow_grid = None

        self.close_behind_you = False

        self.fake_window = fake_window

    def stop(self):
        self.close_behind_you = True
        self.check_closing()

    def on_closing(self):
        self.close_behind_you = True

    def run(self):
        if self.fake_window:
            while not self.close_behind_you:
                pass

        else:
            self.window = Tk()
            self.canvas = Canvas(self.window, width=self.width, height=self.height, background='white')
            self.canvas.pack()

            # Display the buoys
            self.display_buoys()

            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.window.mainloop()

            self.canvas = None

    def display_buoys(self):
        color = "red"
        for buoy in self.buoys:
            x0 = buoy.pos[0]-buoy.valid_dist/2
            y0 = buoy.pos[1]-buoy.valid_dist/2
            x1 = buoy.pos[0]+buoy.valid_dist/2
            y1 = buoy.pos[1]+buoy.valid_dist/2
            x0, y0 = simu_to_tk_coords(x0, y0, self.width, self.height)
            x1, y1 = simu_to_tk_coords(x1, y1, self.width, self.height)
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color, width=3)

    def check_closing(self):
        if self.close_behind_you and self.window is not None:
            self.window.quit()

    def display(self, ts, boats, wind_direction_table, wind_speed_table):
        if self.canvas is None:
            return

        if self.ts is not None and time.time() - self.ts < self.dt:
            return
        else:
            self.ts = time.time()

        if self.arrow_grid is None:
            self.arrow_grid = []
            for i in range(len(wind_direction_table)):
                line = []
                xw = (i+0.5) * self.height / len(wind_direction_table)
                for j in range(len(wind_direction_table[0])):
                    yw = (j+0.5) * self.width / len(wind_direction_table[0])
                    line.append(ArrowDraw(self.canvas, self.width, self.height, xw, yw, 0, 0))
                self.arrow_grid.append(line)

        for i in range(len(wind_direction_table)):
            for j in range(len(wind_direction_table[0])):
                self.arrow_grid[i][j].redraw(wind_direction_table[i, j], wind_speed_table[i, j])

        for boat in boats:
            if boat.name not in self.boats:
                color = "black" if "Noob" in boat.name else "blue"
                self.boats[boat.name] = BoatDraw(self.canvas, boat.pos[0], boat.pos[1], boat.yaw, boat.helm_angle, self.width, self.height, color)
            else:
                self.boats[boat.name].redraw(boat.pos[0], boat.pos[1], boat.yaw, boat.helm_angle)

        self.check_closing()
