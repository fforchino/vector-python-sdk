#!/bin/bash

whoami
sudo -i -u pi bash << EOF
/home/pi/vector-python-sdk/wirepod/$1.py "${@:2}"
EOF
echo "Out"
whoami

