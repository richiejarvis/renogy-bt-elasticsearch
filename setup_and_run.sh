#!/bin/bash
#
# This script moves my real config.ini into place
# Sets up the Python Env and runs the program
# On exit, it deactivates the Python Env and
# Moves the config.ini's back to the original place

# Setup Python Env
# Check if there is one already
# Create and install the dependancies if not there
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/richie/git/allsky/scripts
MY_PATH="/home/richie/git/renogy-bt-elasticsearch"
if [ ! -d "$MY_PATH/venv" ]
then
	python -m venv "$MY_PATH/venv"
fi
# Might as well update the requirements to see if there are any updates
source "$MY_PATH/venv/bin/activate"
# Did the venv initialise OK?
if [ $? -eq 0 ]; then
	pip install -r "$MY_PATH/requirements.txt" -U
	# Let's save the config.ini to config.ini.blank so our credentials isn't exposed
	# We can copy in the .gitignored config.ini.private to config.ini temporarily
	if [ -f "$MY_PATH/config.ini.private" ]; then
		cp "$MY_PATH/config.ini.private" "$MY_PATH/config.ini"
	fi
	# For safety, reset the bluetooth adaptor in case it got stuck again!
	sudo hciconfig hci0 reset
	# We should be ready to run now
	python "$MY_PATH/example.py"
fi

# We finished!  Let's copy the original blank config.ini back
if [ -f "$MY_PATH/config.ini.blank" ]; then
	cp "$MY_PATH/config.ini.blank" "$MY_PATH/config.ini"
fi
        	



