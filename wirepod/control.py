# Import a library of functions called 'pygame'
import pygame
import anki_vector
import sys, os, glob
import time
import requests

PEER_IP_ADDRESS = "192.168.43.196"
SPEED_MAX = 180

# Initialize the game engine
pygame.init()
clock = pygame.time.Clock()


#        robot.motors.set_lift_motor(0)
#        robot.motors.set_head_motor(0)
#        robot.motors.stop_all_motors()

done = False

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    # No joysticks!
    print("Error, I didn't find any joysticks.")

joystick = pygame.joystick.Joystick(0)
joystick.init()

name = joystick.get_name()
print("Using joystick name: {}".format(name))
buttons = joystick.get_numbuttons()
print("Number of buttons: {}".format(buttons))

left = 0
right = 0
fw = 0

w = 700
h = 500
size = [w, h]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("My Game")

def movePeer(leftEngine, rightEngine):
  l = (int)(leftEngine * 100 / SPEED_MAX);
  r = (int)(rightEngine * 100 / SPEED_MAX);
  reqUrl = "http://"+PEER_IP_ADDRESS+"/motor?l="+str(l)+"&r="+str(r)
  #print(reqUrl)
  requests.get(reqUrl)
  

with anki_vector.Robot(cache_animation_lists=False) as robot:
    robot.motors.stop_all_motors()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        #print("Axis {:.2f}/{:.2f}".format(x,y))
        
        if x<-0.5:
            left = 0
            right = fw/2
        elif x>0.5:
            left = fw/2
            right = 0
        else :
            left = 0
            right = 0
        
        if y<-0.5:
            left = right = 0
            if fw<0:            
                fw = 0
            else:
                fw = min(fw + 10, SPEED_MAX)
        elif y>0.5:
            left = right = 0
            if fw>0: 
                fw = 0
            else:
                fw = max(fw - 10, -SPEED_MAX)
      
        b0 = joystick.get_button(0)
        b1 = joystick.get_button(1)
        b2 = joystick.get_button(2)
        b3 = joystick.get_button(3)
        b4 = joystick.get_button(4)
        b5 = joystick.get_button(5)
        b6 = joystick.get_button(6)
        b7 = joystick.get_button(7)
        b8 = joystick.get_button(8)
        b9 = joystick.get_button(9)
        
        #print("Buttons: "+str(b0)+
        #                 str(b1)+
        #                 str(b2)+
        #                 str(b3)+
        #                 str(b4)+
        #                 str(b5)+
        #                 str(b6)+
        #                 str(b7)+
        #                 str(b8)+
        #                 str(b9))

        if b0==1:
           # X quits
           done = True
        if b1==1:
           # A stops all motors
           print("Left {:.2f} Right {:.2f} Forward: {:.2f}".format(left,right,fw))
           fw = 0
           left = 0
           right = 0
           robot.motors.stop_all_motors()
           movePeer(0,0)
        if b2==1:
           # B Shoots
           robot.motors.set_lift_motor(2)
           robot.audio.stream_wav_file("laser2.wav", 75)
           robot.motors.set_lift_motor(-2)
           time.sleep(0.5)
        if b3==1:
           # Y takes a pic
           image = robot.camera.capture_single_image()
           print(f"Displaying image with id {image.image_id}, received at {image.image_recv_time}")           
           mode = image.raw_image.mode
           size = image.raw_image.size
           data = image.raw_image.tobytes()
           py_image = pygame.image.fromstring(data, size, mode)
           rect = py_image.get_rect()
           rect.center = w//2, h//2
           screen.blit(py_image, rect)
           pygame.display.update()                      
           #image.raw_image.show()
        
        if b4==1:
           # DL moves fork up
           ffork = 0.1
        elif b6==1:
           # DL moves fork down
           ffork = -0.1
        else:
           ffork = 0

        rleft = fw+left
        rright = fw+right
        #print("Left {:.2f} Right {:.2f}".format(rleft,rright))
        robot.motors.set_wheel_motors(rleft, rright)    
        robot.motors.set_lift_motor(ffork)
        
        #movePeer(rleft, rright)        
        
        clock.tick(100)        
     
    robot.motors.stop_all_motors()
    #movePeer(0,0)
    pygame.quit()