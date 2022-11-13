#!/usr/bin/env python3

"""
Turns on or off the lights
"""

import pyparticle as pp
import sys

def main():
    if len(sys.argv)>0:
        action = sys.argv[1]
        #Generate access token here: https://docs.particle.io/reference/cloud-apis/access-tokens/#create-a-token-browser-based-
        particle = pp.Particle(access_token="7243681a6a7b7566ed268c5481b01c8b5d2746fe")
        
        #List devices
        devices = particle.list_devices()
        print('Found %d device(s)' % len(devices))
    
        i = 0
        selected = ""   
        for device in devices:
            if (device['name']=="Alphonso"):
                selected = device['id']
                selectedDevice = device

        if (selected!=""): 
            print('Selected device %s' % selected)
            func_call_result = particle.call_function(selectedDevice['id'], 'switch', action)
            print('Func call result: %d' % func_call_result)
    else:
        print("USAGE: lights.py <on|off>")
    
if __name__ == "__main__":
    main()


