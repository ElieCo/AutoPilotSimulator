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

MEAS_NB_SIMU = 10

WIDTH = 1000
HEIGHT = 1000

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--nooboat', help="set the number of nooboat", type=int, default=10, required=False)
    parser.add_argument('--measure', help="measure the mean duration your boat need finish the run", action="store_true")
    args = parser.parse_args()

    nooboat_nb = args.nooboat
    if args.measure:
        nooboat_nb = 0
        print("Wait, it will perform %i simulations to have the mean duration your pilot need to finish this run." % MEAS_NB_SIMU)

    boats = []
    start_pos = np.array([50, 500], dtype="float")

    # Init Nooboats
    if nooboat_nb > 0:
        for i in range(nooboat_nb - 1):
            boats.append(Boat(NoobPilot(), "Noob" + str(i), start_pos))
        boats.append(Boat(ChampiNoobPilot(), "ChampiNoob", start_pos))

    # Init route
    buoys = []
    valid_dist = 5
    buoys.append(Buoy(800, 500, valid_dist))
    buoys.append(Buoy(800, 300, valid_dist))
    buoys.append(Buoy(50, 300, valid_dist))
    buoys.append(Buoy(50, 500, valid_dist))
    buoys.append(Buoy(800, 500, valid_dist))
    buoys.append(Buoy(800, 300, valid_dist))
    buoys.append(Buoy(50, 300, valid_dist))
    buoys.append(Buoy(50, 500, valid_dist))

    # Init displayer with the buoys
    displayer = Displayer(0.05, buoys, WIDTH, HEIGHT, args.measure)
    displayer.start()

    # If this is a measure, make 10 simulations
    nb_simu = 10 if args.measure else 1
    ts_measured = []
    for _ in range(nb_simu):

        # Init player boat
        player = Boat(PlayerPilot(), "Player", start_pos)
        boats.append(player)

        # Init wind manager
        eole = Eole(0, 10, WIDTH, HEIGHT, 100)

        # Start simulation
        dt = 0.1
        if args.measure:
            dt = 1
        ts = 0
        speed = 50
        timeout = 6000000
        while ts <= timeout and not player.all_buoys_reached and displayer.is_alive():
            # Update timestamp
            ts += dt

            # Update wind
            eole.update(dt)

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
            displayer.display(ts, boats, eole.get_direction_grid(), eole.get_speed_grid())

            # Sleep the necessary time
            if not args.measure:
                time.sleep(float(dt)/speed)

        ts_measured.append(ts)

    if args.measure:
        displayer.stop()
        print("The mean duration is: %.3f" % np.mean(ts_measured))

    # Wait that the player close the window
    while displayer.is_alive():
        displayer.check_closing()
        time.sleep(0.1)
