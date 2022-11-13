#!/usr/bin/env python3

import sys, os, glob
import time
import requests

PEER_IP_ADDRESS = "192.168.43.196"
SPEED_MAX = 100

def movePeer(leftEngine, rightEngine):
  l = (int)(leftEngine * 100 / SPEED_MAX);
  r = (int)(rightEngine * 100 / SPEED_MAX);
  reqUrl = "http://"+PEER_IP_ADDRESS+"/motor?l="+str(l)+"&r="+str(r)
  #print(reqUrl)
  requests.get(reqUrl)
  
def lightOp(isOn):
  reqUrl = "http://"+PEER_IP_ADDRESS+"/light?on="+str(isOn)
  #print(reqUrl)
  requests.get(reqUrl)

def stop():
  movePeer(0,0)

movePeer(58,50)
time.sleep(3)
stop()
time.sleep(3)
lightOp(1)
time.sleep(0.05)
lightOp(0)
time.sleep(2)

done = False
i = 1
while i<3:
   lightOp(1)
   time.sleep(0.05)
   i = i + 1
   lightOp(0)

lightOp(1)



