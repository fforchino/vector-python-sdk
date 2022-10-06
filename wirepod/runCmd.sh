#!/bin/bash

cmd="/home/pi/vector-python-sdk/wirepod/$1.py \"${@:2}\""
echo $cmd
runuser -l pi -c "$cmd"
echo "Out"
