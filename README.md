# AutoPilotSimulator

You like coding?

You like sailing?

Well, you're in the right place! Here, you will make your code sail...

# How to code your Pilot

To be automaticaly include in the game, you have to respect some rules for your coding:
- your pilot have to be coded in a class named PlayerPilot
- this class have to be in a file named "player_code.py" in the directory "player"
- this class have to inherit from AutoPilot, coded in the file src/boat.py
- this class have to overwrite its function update()

All data your pilot have access to are in the dictionnary self.obs
All commands your pilot can control have to be written in the dictionnary self.cmd
See the AutoPilot constructor to know the contents of those dictionnaries.

Rename "player/player_code_example.py" in "player/player_code.py" to run an example.

# How to get some help

See the --help option.

# How to do a measure

Run the --measure option and it will return the mean duration that your boat need to finish a run.
