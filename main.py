import numpy as np
import sys
import time
import argparse
import os

from src.eole import Eole
from src.displayer import Displayer
from src.boat import NoobPilot, ChampiNoobPilot, Boat
from src.buoy import Buoy

if not os.path.exists("player/player_code.py"):
    print("Error: You should create in the \"player\" directory a "
    "file called \"player_code.py\" containing a class called \"PlayerPilot\" "
    "which inheritate of \"src.boat.AutoPilot\"")
    exit(-1)

from player.player_code import PlayerPilot

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
    boats.append(Boat(ChampiNoobPilot(), "ChampiNoob"))

    # Init player boat
    player = Boat(PlayerPilot(), "Player")
    boats.append(player)

    # Init wind manager
    eole = Eole(0, 5)

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
    timeout = 6000000
    while ts <= timeout and not player.all_buoys_reached and displayer.is_alive():
        # Update timestamp
        ts += dt

        # Update data of every boat
        for boat in boats:
            # Get wind for this boat
            wind = eole.get_wind_at(boat.pos)

            # Update data
            boat.updatePilot(wind, buoys, boats)

        # Ask the decision of the player boat

        # Move all boats
        for boat in boats:
            boat.move(dt)

        # Display
        displayer.display(ts, boats, None)

        # Sleep the necessary time
        time.sleep(float(dt)/speed)

    # Wait that the player close the window
    while displayer.is_alive():
        displayer.check_closing()
        time.sleep(0.1)
