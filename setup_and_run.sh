#!/bin/bash
#
# This script moves my real config.ini into place
# Sets up the Python Env and runs the program
# On exit, it deactivates the Python Env and
# Moves the config.ini's back to the original place

# Setup Python Env
# Check if there is one already
# Create and install the dependancies if not there
if [ ! -d venv ]; then
	python -m venv venv
fi
# Might as well update the requirements to see if there are any updates
source ./venv/bin/activate
# Did the venv initialise OK?
if [ $? -eq 0 ]; then
	pip install -r requirements.txt -U
	# Let's save the config.ini to config.ini.blank so our credentials isn't exposed
	# We can copy in the .gitignored config.ini.private to config.ini temporarily
	if [ -f config.ini.private ]; then
		cp config.ini.private config.ini
	fi
	# We should be ready to run now
	python example.py
fi

# We finished!  Let's copy the original blank config.ini back
if [ -f config.ini.blank ]; then
	cp config.ini.blank config.ini
fi
        	



