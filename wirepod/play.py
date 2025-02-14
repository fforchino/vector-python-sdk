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
# distributed under the License isvi distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Play audio files through Vector's speaker.
USAGE: play.py <intro message>;<volume 0..100>;<audiopath>;<filename or '*'>
E.g. ./play.py Rock and roll;75;/home/pi/AUDIOFILES;song01.wav
     Plays /home/pi/AUDIOFILES/song01.wav File is converted in the right format before being played
E.g. ./play.py ' ;75;/home/pi/AUDIOFILES;*'
     Plays a random song file located in /home/pi/AUDIOFILES File is converted in the right format before being played
"""

import anki_vector
import sys, os, glob
from pydub import AudioSegment

def main():
    with anki_vector.Robot(cache_animation_lists=False) as robot:
        audioFile = ""
        args = sys.argv[1]
        print ("---"+args+"---")
        args = args[1:]
        args = args[:-1]
        args = args.split(";")
                
        introMessage = args[0]
        volume = int(args[1])
        audioPath = args[2]
        target = args[3]
        
        print ("introMessage "+introMessage)
        print ("volume "+str(volume))
        print ("audioPath "+audioPath)
        print ("target "+target)

        dst = "test.wav"
        if os.path.exists(dst):
            os.remove(dst)
  
        if target=="*": 
            files = glob.glob(os.path.join(audioPath, '*'))
            from random import randrange
            i = randrange(len(files))
            print("Play random " + str(i) +"/"+str(len(files)))
            audioFile = files[i]
            sound = AudioSegment.from_file(audioFile)
            sound = sound.set_frame_rate(8000)
            sound = sound.set_sample_width(2)
            sound = sound.set_channels(1)
            sound.export(dst, format="wav")
            audioFile = dst
        else:
            audioFile = os.path.join(audioPath, target) 
            sound = AudioSegment.from_file(audioFile)
            sound = sound.set_frame_rate(8000)
            sound = sound.set_sample_width(2)
            sound = sound.set_channels(1)
            sound.export(dst, format="wav")
            audioFile = dst
        
        print("Play " + audioFile)
        
        if len(introMessage.strip())>0:
            robot.behavior.say_text(introMessage)
        
        robot.audio.stream_wav_file(audioFile, volume)


if __name__ == "__main__":
    main()
