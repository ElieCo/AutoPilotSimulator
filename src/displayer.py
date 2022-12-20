from tkinter import *
from threading import Thread
import numpy as np

def simu_to_tk_coords(x, y):
    return x + 500, 500 - y

class BoatDraw:
    def __init__(self, canvas, x, y, yaw, helm_angle, color="black"):
        self.canvas = canvas
        self.color = color

        self.poly = self.canvas.create_polygon(0, 0, fill=color, outline=color, width=3)
        self.redraw(x, y, yaw, helm_angle)

    def redraw(self, x, y, yaw, helm_angle):
        self.canvas.coords(self.poly, *self.getPolygonCoords(x, y, yaw, helm_angle))

    def getPolygonCoords(self, x, y, yaw, helm_angle):

        x, y = simu_to_tk_coords(x, y)

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

        return xh, yh, x, y, x2, y2, x1, y1, x3, y3, x, y


class Displayer(Thread):
    def __init__(self, display_dt_s):
        Thread.__init__(self)

        self.canvas = None

        self.dt = display_dt_s
        self.ts = None
        self.boats = {}

    def init_window(self):
        self.window = Tk()
        self.canvas = Canvas(self.window, width=1000, height=1000, background='white')
        self.canvas.pack()

    def run(self):
        self.init_window()
        self.window.mainloop()

    def display(self, ts, marks, boats, wind_table):
        if self.canvas is None:
            return

        if self.ts is not None and ts - self.ts < self.dt:
            return
        else:
            self.ts = ts

        for boat in boats:
            if boat.name not in self.boats:
                color = "black" if "Noob" in boat.name else "blue"
                self.boats[boat.name] = BoatDraw(self.canvas, boat.pos[0], boat.pos[1], boat.yaw, boat.helm_angle, color)
            else:
                self.boats[boat.name].redraw(boat.pos[0], boat.pos[1], boat.yaw, boat.helm_angle)
