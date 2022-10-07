#!/usr/bin/env python3

# Copyright (c) 2018 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Move
USAGE: move.py [trick number]
E.g. ./move.py 0
Plays a dance trick. Plays a random trick if no trick number is passed
"""

import anki_vector
import sys, os, glob
import time

def main():
    movement = [
        [
            "500%0%1%1%0",
            "500%0%1%-1%0",
            "500%0%1%1%0",
            "-500%0%1%-1%0",
            "-500%0%1%1%0",
            "-500%0%1%-1%0"
        ],
        [
            "90%0%1%0%0", 
            "0%90%1%0%0",
            "90%0%1%0%0", 
            "0%90%1%0%0",
            "90%0%1%0%0", 
            "0%90%1%0%0",
            
            "0%-90%1%0%0",
            "-90%0%1%0%0", 
            "0%-90%1%0%0",
            "-90%0%1%0%0", 
            "0%-90%1%0%0",
            "-90%0%1%0%0"
        ],
        [
            "0%0%1%0%1", 
            "0%0%1%0%-1", 
            "0%0%1%0%1", 
            "0%0%1%0%-1", 
            "0%0%1%0%1", 
            "0%0%1%0%-1", 
            "0%0%1%0%1", 

            "0%0%1%1%-1", 
            "0%0%1%-1%1", 
            "0%0%1%1%-1", 
            "0%0%1%-1%1", 
            "0%0%1%1%-1", 
            "0%0%1%-1%1"
        ],
        [
            "90%0%1%1%0", 
            "0%90%1%-1%0",
            "-90%0%1%1%0", 
            "0%-90%1%-1%0"
            "90%0%1%1%0", 
            "0%90%1%-1%0",
        ]
    ]

    r = -1
    if len(sys.argv)>1 and len(sys.argv[1])>0:
        r = int(sys.argv[1]) 
        if r>len(movement):
            r = len(movement)-1
    
    if r==-1: 
        from random import randrange
        r = randrange(len(movement))

    #Debug 
    #r = 0
    
    with anki_vector.Robot(cache_animation_lists=False) as robot:
        i = 0
        moves = movement[r]
        for m in moves:
            movs = m.split("%")
            robot.motors.set_wheel_motors(int(movs[0]), int(movs[1]))
            robot.motors.set_lift_motor(float(int(movs[3])))
            robot.motors.set_head_motor(float(int(movs[4])))            
            time.sleep(float(int(movs[2])))
            i = i + 1
            
        robot.motors.set_wheel_motors(0,0)    
        robot.motors.set_lift_motor(0)
        robot.motors.set_head_motor(0)
        robot.motors.stop_all_motors()
    
if __name__ == "__main__":
    main()
