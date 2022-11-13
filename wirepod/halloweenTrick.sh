#!/bin/bash

cd /home/pi/vector-python-sdk/wirepod
runuser -l pi -c "/home/pi/vector-python-sdk/wirepod/halloween.py" &
runuser -l pi -c "/home/pi/vector-python-sdk/wirepod/halloween_vector.py" &
