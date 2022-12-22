import numpy as np
import sys
import time
import argparse

sys.path.append("src")
from eole import Eole
from displayer import Displayer
from boat import NoobPilot, Boat

class Buoy:
    def __init__(self, x, y, valid_dist):
        self.pos = np.array([float(x), float(y)])
        self.valid_dist = valid_dist


if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--nooboat', help="set the number of nooboat", type=int, default=10, required=False)
    args = parser.parse_args()

    nooboat_nb = args.nooboat

    boats = []

    # Init Nooboats
    for i in range(nooboat_nb):
        boats.append(Boat(NoobPilot(), "Noob" + str(i)))

    # Init player boat

    # Init wind manager
    eole = Eole()

    # Init route
    buoys = []
    valid_dist = 5
    buoys.append(Buoy(0, 800, valid_dist))
    buoys.append(Buoy(-200, 800, valid_dist))
    buoys.append(Buoy(-200, 0, valid_dist))
    buoys.append(Buoy(0, 0, valid_dist))
    buoys.append(Buoy(0, 800, valid_dist))
    buoys.append(Buoy(-200, 800, valid_dist))
    buoys.append(Buoy(-200, 0, valid_dist))
    buoys.append(Buoy(0, 0, valid_dist))

    # Init displayer with the buoys
    displayer = Displayer(0.1, buoys)
    displayer.start()

    # Start simulation
    dt = 0.1
    ts = 0
    speed = 100
    duration = 600000
    while ts <= duration and displayer.is_alive():
        # Update timestamp
        ts += dt

        # Update data of every boat
        for boat in boats:
            boat.updatePilot([np.radians(90), 5], buoys, None)

        # Move all boats
        for boat in boats:
            boat.move(dt)

        # Display
        displayer.display(ts, boats, None)

        # Ask the decision of the player boat

        # Sleep the necessary time
        time.sleep(float(dt)/speed)

    # Stop and wait the displayer
    displayer.stop()
    displayer.join()
