#!/bin/bash

runuser -l pi -c "/home/pi/vector-python-sdk/wirepod/lights.py on &"
runuser -l pi -c "/home/pi/vector-python-sdk/wirepod/play.py ' ;75;/home/pi/vector-python-sdk/wirepod;fx.wav '" 
