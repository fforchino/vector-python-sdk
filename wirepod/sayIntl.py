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
USAGE: sayIntl.py <language: it|en> [sentence]
E.g. ./say.py en "Hello Filippo"
     ./say.py it
Says a random wisdom sentence if no sentence is passed
"""

import anki_vector
import sys
from pydub import AudioSegment
from gtts import gTTS
from random import randrange

def main():
    sentences_en = [
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

    sentences_it = [
            "Tanto va la gatta al lardo che ci lascia lo zampino", 
            "La gatta frettolosa ha fatto i gattini ciechi", 
            "L'erba del vicino è sempre più verde",
            "Chi lascia la via vecchia per la nuova sa quello che perde ma non quello che trova", 
            "Volere è potere", 
            "A caval donato non si guarda in bocca",
            "Mogli e buoi dei paesi tuoi", 
            "Nella botte piccola c'è il vino buono", 
            "Mal comune mezzo gaudio",
            "La madre degli stolti è sempre incinta"
            ] 

    with anki_vector.Robot(cache_animation_lists=False) as robot:        
        phrase = ""
        if len(sys.argv)==3:
            phrase = sys.argv[2]
        language = sys.argv[1]
        if language=="it":
            sentences = sentences_it
        else:
            sentences = sentences_en
                
        if len(phrase)==0: 
            i = randrange(len(sentences))
            phrase = sentences[i]

        print("Say " + phrase + " in language: "+language)
        
        audioFileMp3 = "/home/pi/tts.mp3"
        audioFileWav = "/home/pi/tts.wav"
        tts = gTTS(phrase, lang=language)
        tts.save(audioFileMp3)
        
        sound = AudioSegment.from_file(audioFileMp3)
        sound = sound.set_frame_rate(8000)
        sound = sound.set_sample_width(2)
        sound = sound.set_channels(1)
        sound.export(audioFileWav, format="wav")
        
        print("Play " + audioFileWav)
        
        robot.audio.stream_wav_file(audioFileWav, 75)

if __name__ == "__main__":
    main()
