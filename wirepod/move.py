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
USAGE: move.py
E.g. ./move.py
"""

import anki_vector
import sys
import time

def main():
    movement = [
            "90%0%1%1", 
            "0%90%1%-1",
            "-90%0%1%1", 
            "0%-90%1%-1"
            ] 

    with anki_vector.Robot(cache_animation_lists=False) as robot:
        i = 0
        for m in movement:
            movs = m.split("%")
            robot.motors.set_lift_motor(float(int(movs[3])))
            robot.motors.set_wheel_motors(int(movs[0]), int(movs[1]))
            time.sleep(float(int(movs[2])))
            i = i + 1
            
        robot.motors.stop_all_motors()
        robot.motors.set_lift_motor(0)
    
if __name__ == "__main__":
    main()
