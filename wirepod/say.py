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
Say a sentence
USAGE: say.py [sentence]
E.g. ./say.py 'Hello Filippo'
Says a random wisdom sentence if no sentence is passed
"""

import anki_vector
import sys

def main():
    sentences = [
            "Fortune favors the bold", 
            "I think, therefore I am", 
            "Time is money",
            "I came, I saw, I conquered", 
            "When life gives you lemons, make lemonade", 
            "Practice makes perfect",
            "Knowledge is power", 
            "Have no fear of perfection, you'll never reach it", 
            "No pain no gain",
            "That which does not kill us makes us stronger"
            ] 

    with anki_vector.Robot(cache_animation_lists=False) as robot:        
        phrase = ""
        if len(sys.argv)>0:
            phrase = sys.argv[1]
        
        if len(phrase)==0: 
            from random import randrange
            i = randrange(10)
            phrase = sentences[i]

        print("Say " + phrase)
        robot.behavior.say_text(phrase, False)

if __name__ == "__main__":
    main()
