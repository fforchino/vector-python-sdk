#!/bin/bash

echo $1
cmd1="gtts-cli \"$1\" --lang it --output /home/pi/ita.mp3"
cmd2="python3 /home/pi/vector-python-sdk/wirepod/play.py \"' ;75;/home/pi;ita.mp3'\""
echo $cmd
runuser -l pi -c "$cmd1"
runuser -l pi -c "$cmd2"
echo "Out"
