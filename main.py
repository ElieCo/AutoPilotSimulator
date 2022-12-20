import numpy as np
import sys
import time
import argparse

sys.path.append("src")
from eole import Eole
from displayer import Displayer
from boat import NoobPilot, Boat


if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--nooboat', help="set the number of nooboat", type=int, default=1, required=False)
    args = parser.parse_args()

    nooboat_nb = args.nooboat

    boats = []

    # Init Nooboats
    for i in range(nooboat_nb):
        boats.append(Boat(NoobPilot(), "Noob" + str(i)))

    # Init player boat

    # Init wind manager
    eole = Eole()

    # Init displayer
    displayer = Displayer(0.1)
    displayer.start()

    # Init route

    # Start simulation
    dt = 0.1
    ts = 0
    speed = 1
    duration = 20
    while ts <= duration:
        # Update timestamp
        ts += dt

        # Move all boats

        # Update data of the player boat
        boats[0].yaw += np.radians(1)

        # Display
        displayer.display(ts, None, boats, None)

        # Ask the decision of the player boat

        # Sleep the necessary time
        time.sleep(float(dt)/speed)
