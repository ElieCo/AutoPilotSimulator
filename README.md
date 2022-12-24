# AutoPilotSimulator

Do you like coding?
Do you like sailing?
So you're on right place! Here, you will make your code sail...

# How to code your Pilot

To be automaticaly include in the game, you have to respect some rules for your coding:
- your pilot have to be coded in a class named PlayerPilot
- this class have to inherit from AutoPilot in the file src/boat.py
- this class have to overwrite the function update()

All data your pilot have access to are in the dictionnary self.obs
All commands your pilot controls have to be written in the dictionnary self.cmd
See the AutoPilot constructor to know the contents of those dictionnaries.

# How to get some help

See the --help option.

# How to do a measure

Run the --measure option and it will return the mean duration that your boat need to finish a run.
