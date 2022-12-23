import numpy as np
import sys
import time
import argparse

sys.path.append("src")
from eole import Eole
from displayer import Displayer
from boat import NoobPilot, ChampiNoobPilot, Boat
from buoy import Buoy

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
    boats.append(Boat(ChampiNoobPilot(), "Champi"))

    # Init wind manager
    eole = Eole()

    # Init route
    buoys = []
    valid_dist = 5
    buoys.append(Buoy(800, 0, valid_dist))
    buoys.append(Buoy(800, -200, valid_dist))
    buoys.append(Buoy(0, -200, valid_dist))
    buoys.append(Buoy(0, 0, valid_dist))
    buoys.append(Buoy(800, 0, valid_dist))
    buoys.append(Buoy(800, -200, valid_dist))
    buoys.append(Buoy(0, -200, valid_dist))
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
            # Get wind for this boat
            wind = [np.radians(0), 5]

            # Update data
            boat.updatePilot(wind, buoys, boats)

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
