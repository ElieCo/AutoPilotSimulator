import numpy as np
import sys
import time
import argparse
import os

# Import simulation objects
from src.eole import Eole
from src.displayer import Displayer
from src.boat import NoobPilot, ChampiNoobPilot, Boat
from src.buoy import Buoy

# Check if the player have done his/her homework
if not os.path.exists("player/player_code.py"):
    print("Error: You should create in the \"player\" directory a "
    "file called \"player_code.py\" containing a class called \"PlayerPilot\" "
    "which inheritate of \"src.boat.AutoPilot\"")
    exit(-1)

# Import player's code
from player.player_code import PlayerPilot

# Number of simulations needed to do a measure
MEAS_NB_SIMU = 10

# Size of the map
WIDTH = 1000
HEIGHT = 1000

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--nooboat', help="set the number of nooboat", type=int, default=10, required=False)
    parser.add_argument('--measure', help="measure the mean duration your boat need finish the run", action="store_true")
    args = parser.parse_args()

    # Get the number of Nooboat asked
    nooboat_nb = args.nooboat
    # If a mesaure is asked, don't spend time with the nooboat
    if args.measure:
        nooboat_nb = 0
        print("Wait, it will perform %i simulations to have the mean duration your pilot need to finish this run." % MEAS_NB_SIMU)

    # Init the list of all boats
    boats = []
    # Init the start position
    start_pos = np.array([50, 500], dtype="float")

    # Init Nooboats
    if nooboat_nb > 0:
        # Create one nooboat better that the others
        boats.append(Boat(ChampiNoobPilot(), "ChampiNoob", start_pos))
        for i in range(nooboat_nb - 1):
            boats.append(Boat(NoobPilot(), "Noob" + str(i), start_pos))

    # Init player boat
    player = Boat(PlayerPilot(), "Player", start_pos)
    boats.append(player)

    # Init the course
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
    ts_measured = [] # List of the duration the player needed to finish the course
    for _ in range(nb_simu):

        # At the begin of each simulation, reset the player's boat
        player.reset(start_pos)

        # At the begin of each simulation, init wind manager
        eole = Eole(0, 10, WIDTH, HEIGHT, 100)

        # Set the dt (delta time between two step of simulation)
        #  If it's a measure, increase dt to reduce calculation duration
        dt = 0.1 if not args.measure else 1
        # Init the timestamp at 0 (time spent since the begining of this simulation in seconds)
        ts = 0
        # Init the speed of the simulation (1 for realtime, 2 for twice the realtime speed)
        speed = 50
        # Set a timeout in case the player fail to finish the course
        timeout = 6000000 # TODO: [EC] Find a more realistic value and add a option to set it

        # Start simulation
        # Run the simulation while the timeout is not reached,
        #  the player haven't finish the course or closed the window
        while ts <= timeout and not player.all_buoys_reached and displayer.is_alive():
            # Update the timestamp
            ts += dt

            # Update wind
            eole.update(dt)

            # Update data of every boat
            for boat in boats:
                # Get wind for this boat
                wind = eole.get_wind_at(boat.pos)

                # Update data
                boat.update(wind, buoys, boats)

            # Move all boats
            for boat in boats:
                boat.move(dt)

            # Display
            displayer.display(ts, boats, eole.get_direction_grid(), eole.get_speed_grid())

            # Sleep the necessary time (except if this the a measure)
            if not args.measure:
                time.sleep(float(dt)/speed)

        # Add the timestamp to the list of measured ts
        ts_measured.append(ts)

    # If this is a measure, stop the displayer thread and print the result
    if args.measure:
        displayer.stop()
        print("The mean duration is: %.3f" % np.mean(ts_measured))

    # Wait that the player close the window
    while displayer.is_alive():
        displayer.check_closing()
        time.sleep(0.1)
