from tkinter import *
from threading import Thread
import numpy as np

WIDTH = 1000
HEIGHT = 1000

def simu_to_tk_coords(x, y):
    return y + WIDTH/2, HEIGHT - 50 - x

class BoatDraw:
    def __init__(self, canvas, x, y, yaw, helm_angle, color="black"):
        self.canvas = canvas
        self.color = color

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

        x, y = simu_to_tk_coords(x, y)
        x1, y1 = simu_to_tk_coords(x1, y1)
        x2, y2 = simu_to_tk_coords(x2, y2)
        x3, y3 = simu_to_tk_coords(x3, y3)
        xh, yh = simu_to_tk_coords(xh, yh)

        return xh, yh, x, y, x2, y2, x1, y1, x3, y3, x, y


class Displayer(Thread):
    def __init__(self, display_dt_s, buoys, fake_window=False):
        Thread.__init__(self)

        self.window = None
        self.canvas = None

        self.dt = display_dt_s
        self.ts = None
        self.boats = {}
        self.buoys = buoys

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
            self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT, background='white')
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
            x0, y0 = simu_to_tk_coords(x0, y0)
            x1, y1 = simu_to_tk_coords(x1, y1)
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color, width=3)

    def check_closing(self):
        if self.close_behind_you and self.window is not None:
            self.window.quit()

    def display(self, ts, boats, wind_table):
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

        self.check_closing()
