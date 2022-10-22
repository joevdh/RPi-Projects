#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Wavefront obj model loading. Material properties set in mtl file.
Uses the import pi3d method to load *everything*
"""

import pi3d
import RPi.GPIO as GPIO
import csv
import time
import pygame
import mathutils
from math import radians
from math import degrees
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import threading
import random
import ultrasonic_distance as dist
import socket

# Global Constants
port = 10056
my_socket = socket.socket()

MovementScale = 2.54
ModelScale = 0.005
ImageWidth = 500
ImageHeight = 375

LookAtCenterX = 191
LookAtCenterY = 258
LookAtPitchScale = 30
LookAtYawScale = 20
LookAtSpeedScale = 0.2

FacesDetectedCount = 0
FacesDetectedDuration = 0
LastFaceDetectTime = time.time()
LastFaceDetectedTimeOut = 2

FrameRate = 30
TimeStep = 1.0 / FrameRate

TriggerDistance = 50
TriggerCount = 0

AnywaysAnims = [ 'Anyways1', 'Anyways2', 'Anyways3' ]
ComeBackAnims = [ 'ComeBack1', 'ComeBack2', 'ComeBack3', 'ComeBack4', 'ComeBack5', 'ComeBack6' ]
FidgetAnims = [ 'Fidget1', 'Fidget2', 'Fidget3' ]
GoAwayAnims = [ 'GoAway1', 'GoAway2', 'GoAway3' ]
GoodbyeAnims = [ 'Goodbye1', 'Goodbye2', 'Goodbye3']
GreetingAnims = [ 'Greeting1', 'Greeting2', 'Greeting3' ]
IntroAnims =[ 'Intro1', 'Intro2' ]
NextUpAnims = [ 'NextUp1', 'NextUp2', 'NextUp3' ]
PromptTriggerAnims = [ 'PromptTrigger1', 'PromptTrigger2', 'PromptTrigger3', 'PromptTrigger4' ]
TriggerAnims = [ 'Trigger1', 'Trigger2', 'Trigger3', 'Trigger4', 'Trigger5' ]
YourLossAnims = [ 'YourLoss1', 'YourLoss2', 'YourLoss3', 'YourLoss4' ]

# Global Variables
AnimList = {}
CurrentClip = ''
CurrentAnimData = []
CurrentSound = 0
nFrameIndex = 0
CurrentState = 'Idle'
StateStartTime = 0
WaitTime = 0

DetectionDone = True
FaceBoxes = []
FacePos = []
LastLookAt = [ 0, 0 ]
threads = []

# For Blending
AnimValues = [0,0,0,0,0,0]
LastAnimValues = [0,0,0,0,0,0]
BlendValue = 1
BlendTime = 0.3

pygame.init()

CurrentSound = pygame.mixer.Sound('resources/clips/Idle-Base.wav')

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
#vs = VideoStream(src=0,framerate=1).start()
vs = VideoStream(usePiCamera=True).start()
#time.sleep(2.0)

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, background=(0, 0, 0, 1), frames_per_second=FrameRate)
#DISPLAY = pi3d.Display.create(background=(0, 0, 0, 1), frames_per_second=FrameRate)
shader = pi3d.Shader("uv_bump")

# load model_loadmodel
model_skull = pi3d.Model(file_string='resources/Skull_LowRez2.obj', name='Skull', sx=ModelScale, sy=ModelScale, sz=ModelScale)
model_jaw = pi3d.Model(file_string='resources/Jaw_LowRez2.obj', name='Jaw')
model_skull.add_child(model_jaw)

cam = pi3d.Camera(eye=(0,0,-3.5))

# Fetch key presses
mykeys = pi3d.Keyboard()

def Lerp(src, dst, lerpVal):
    return (src * (1.0-lerpVal)) + (dst * lerpVal)

def CheckCandyTrigger():
    global TriggerCount
    
    currentDist = -1 #dist.distance()
    #print(currentDist)
    if ( currentDist > 0 and currentDist <= TriggerDistance ):
        TriggerCount += 1
    else:
        TriggerCount = 0
        
    return TriggerCount > 3

def run_detection(frame):
    global FaceBoxes
    global DetectionDone
    FaceBoxes = face_recognition.face_locations(frame)
    DetectionDone = True

def LoadAnim(clipName):
    global AnimList
    
    print('Loading ' + clipName)
    
    animData = []
    with open('resources/clips/' + clipName + '.csv') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            animData.append(row)
    
    # Cleanup End of anims
    for i in range(0,60):
        nLastFrame = len(animData)-1
        frameIndex = nLastFrame - (60-i)
        
        lerpVal = float(i) / 60.0
        
        frameData = animData[frameIndex]
        posX = float(frameData[0])
        posY = float(frameData[1])
        posZ = float(frameData[2])
        rotX = float(frameData[3])
        rotY = float(frameData[4])
        rotZ = float(frameData[5])
        
        # Normalize the rotations
        if rotX > 180.0:
            rotX = 360.0 - rotX
        
        if rotY > 180.0:
            rotY = 360.0 - rotY
            
        if rotZ > 180.0:
            rotZ = 360.0 - rotZ
        
        frameData[0] = Lerp(posX, 0.0, lerpVal)
        frameData[1] = Lerp(posY, 0.0, lerpVal)
        frameData[2] = Lerp(posZ, 0.0, lerpVal)
        frameData[3] = Lerp(rotX, 0.0, lerpVal)
        frameData[4] = Lerp(rotY, 0.0, lerpVal)
        frameData[5] = Lerp(rotZ, 0.0, lerpVal)
        animData[frameIndex] = frameData
        
    clip = pygame.mixer.Sound('resources/clips/' + clipName + '.wav')
    
    AnimList[clipName] = [ animData, clip ]

def LoadAllAnims():
    LoadAnim('Idle-Base')
    
    for clipName in AnywaysAnims:
        LoadAnim(clipName)
        
    for clipName in ComeBackAnims:
        LoadAnim(clipName)
        
    for clipName in FidgetAnims:
        LoadAnim(clipName)
        
    for clipName in GoAwayAnims:
        LoadAnim(clipName)
        
    for clipName in GoodbyeAnims:
        LoadAnim(clipName)
        
    for clipName in GreetingAnims:
        LoadAnim(clipName)
        
    for clipName in IntroAnims:
        LoadAnim(clipName)
        
    for clipName in NextUpAnims:
        LoadAnim(clipName)
        
    for clipName in PromptTriggerAnims:
        LoadAnim(clipName)
        
    for clipName in TriggerAnims:
        LoadAnim(clipName)
        
    for clipName in YourLossAnims:
        LoadAnim(clipName)
        
    
def StopAnim():
    global CurrentSound
    global CurrentAnimData
    global CurrentClip
    CurrentSound.play(loops=0)
    CurrentAnimData = []
    CurrentClip = ''
    
def StartAnim(clipName):
    global CurrentClip
    global CurrentSound
    global CurrentAnim
    global CurrentAnimData
    global AnimList
    global nFrameIndex
    global LastAnimValues
    global AnimValues
    global BlendValue
    
    print('Playing ' + clipName)

    CurrentSound.stop()

    CurrentClip = clipName
    CurrentAnimData = AnimList[clipName][0]
    CurrentSound = AnimList[clipName][1]
    CurrentSound.play(loops=0)
    nFrameIndex = 0
    BlendValue = 0
    
    for i in range(0,5):
        LastAnimValues[i] = AnimValues[i]


def UpdateAnim():
    global nFrameIndex
    global BlendValue
    global AnimValues

    if nFrameIndex >= len(CurrentAnimData)-1:
        return True
    
    frameData = CurrentAnimData[nFrameIndex]
    AnimValues[0] = float(frameData[0]) * MovementScale
    AnimValues[1] = float(frameData[1]) * MovementScale
    AnimValues[2] = float(frameData[2]) * MovementScale
    AnimValues[3] = float(frameData[3])
    AnimValues[4] = float(frameData[4])
    AnimValues[5] = float(frameData[5])
    jawRot = float(frameData[6])
    
    if AnimValues[3] > 180.0:
        AnimValues[3] = 360.0 - AnimValues[3]
        
    if AnimValues[4] > 180.0:
        AnimValues[4] = 360.0 - AnimValues[4]
            
    if AnimValues[5] > 180.0:
        AnimValues[5] = 360.0 - AnimValues[5]
    
    BlendValue = min( BlendValue + TimeStep / BlendTime, 1.0 )
    
    posX = Lerp(LastAnimValues[0], AnimValues[0], BlendValue)
    posY = Lerp(LastAnimValues[1], AnimValues[1], BlendValue)
    posZ = Lerp(LastAnimValues[2], AnimValues[2], BlendValue)
    rotX = Lerp(LastAnimValues[3], AnimValues[3], BlendValue)
    rotY = Lerp(LastAnimValues[4], AnimValues[4], BlendValue)
    rotZ = Lerp(LastAnimValues[5], AnimValues[5], BlendValue)
    
    model_skull.xyz = (posZ, posY, -posX)
    model_skull.rxryrz = (-rotX, rotY, 0) #YXZ
    
    model_jaw.rxryrz = (jawRot * -200, 0, 0)
    
    nFrameIndex = min(nFrameIndex + 1, len(CurrentAnimData)-1)
    return nFrameIndex >= len(CurrentAnimData)-1

def LookAtUser():
    rotX = 0
    rotY = 0
    
    #print(FacePos)
    
    if len(FacePos) == 2:
        HalfImageWidth = ImageWidth / 2.0
        HalfImageHeight = ImageHeight / 2.0

        rotX = (FacePos[1] - LookAtCenterY) / HalfImageHeight * LookAtPitchScale
        rotY = (FacePos[0] - LookAtCenterX) / HalfImageWidth * LookAtYawScale
        
    LastLookAt[0] = Lerp(LastLookAt[0], rotX, LookAtSpeedScale)
    LastLookAt[1] = Lerp(LastLookAt[1], rotY, LookAtSpeedScale)
    model_skull.rotateIncX(-LastLookAt[0])
    model_skull.rotateIncY(-LastLookAt[1])

def IdleStart():
    global StateStartTime
    global CurrentState
    
    print('IdleStart')
    CurrentState = 'Idle'
    StateStartTime = time.time()
    StartAnim('Idle-Base')
    
def IdleUpdate():
    global StateStartTime

    if CheckCandyTrigger() == True:
        TriggerCandyStart()
    
    # If we detected a face, go to Greeting
    if FacesDetectedDuration >= 1:
        GreetingStart()
    
    elapsedTime = time.time()- StateStartTime
    if elapsedTime >= 15.0:
        StartAnim(random.choice(FidgetAnims))
        StateStartTime = time.time()

    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IdleStart()
    
def GreetingStart():
    global StateStartTime
    global CurrentState
    
    print('GreetingStart')
    CurrentState = 'Greeting'
    StateStartTime = time.time()
    StartAnim(random.choice(GreetingAnims))
    
def GreetingUpdate():
    if CheckCandyTrigger() == True:
        TriggerCandyStart()
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IntroStart()

def ComeBackStart():
    global StateStartTime
    global CurrentState
    
    print('ComeBack')
    CurrentState = 'ComeBack'
    StateStartTime = time.time()
    StartAnim(random.choice(ComeBackAnims))
    
def ComeBackUpdate():
    bIsAnimFinished = UpdateAnim()
    if CurrentClip != 'Idle-Base' and bIsAnimFinished == True:
        StartAnim('Idle-Base')
    elif CurrentClip == 'Idle-Base':
        if FacesDetectedCount > 0:
            AnywaysStart()
        elif time.time() - StateStartTime > 5:
            YourLossStart()
            
def AnywaysStart():
    global StateStartTime
    global CurrentState
    
    print('Anyways')
    CurrentState = 'Anyways'
    StateStartTime = time.time()
    StartAnim(random.choice(AnywaysAnims))
    
def AnywaysUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IntroStart()
        StartAnim(IntroAnims[1])

def IntroStart():
    global StateStartTime
    global CurrentState
    
    print('IntroStart')
    CurrentState = 'Intro'
    StateStartTime = time.time()
    StartAnim(IntroAnims[0])
     
def IntroUpdate():
    bIsAnimFinished = UpdateAnim()
    
    if CheckCandyTrigger() == True:
        TriggerCandyStart()
    
    if bIsAnimFinished == True:
        #if time.time() - LastFaceDetectTime > LastFaceDetectedTimeOut:
        #    ComeBackStart()
        if CurrentClip == IntroAnims[0]:
            StartAnim(IntroAnims[1])
        elif CurrentClip == IntroAnims[1]:
            WaitTriggerStart()


def WaitTriggerStart():
    global StateStartTime
    global CurrentState
    global WaitTime
    
    print('WaitTriggerStart')
    CurrentState = 'WaitTrigger'
    StateStartTime = time.time()
    WaitTime = time.time()
    StartAnim('Idle-Base')
    
def WaitTriggerUpdate():
    global StateStartTime
    bIsAnimFinished = UpdateAnim()
    
    # If the candy dispensor is triggered, deliver candy
    if CheckCandyTrigger() == True:
        TriggerCandyStart()
        
    elif time.time() - WaitTime > 20:
        YourLossStart()
        
    elif CurrentClip == 'Idle-Base' and time.time() - StateStartTime > 3:
        StartAnim(random.choice(PromptTriggerAnims))
        
    elif bIsAnimFinished == True:
        StartAnim('Idle-Base')
        StateStartTime = time.time()


def YourLossStart():
    global StateStartTime
    global CurrentState
    
    print('YourLossStart')
    CurrentState = 'YourLoss'
    StateStartTime = time.time()
    StartAnim(random.choice(YourLossAnims))
    
def YourLossUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IdleStart()
        

def TriggerCandyStart():
    global StateStartTime
    global CurrentState
    
    print('TriggerCandyStart')
    CurrentState = 'TriggerCandy'
    StateStartTime = time.time()
    StartAnim(random.choice(TriggerAnims))
    
def TriggerCandyUpdate():
    elapsedTime = time.time() - StateStartTime
    #if elapsedTime >= 4 and elapsedTime <= 4.1:
    #    my_socket.send(bytes( "Fire", "UTF-8" ))
        
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        GoodbyeStart()
        my_socket.send(bytes( "Fire", "UTF-8" ))
        

def GoodbyeStart():
    global StateStartTime
    global CurrentState
    
    print('GoodbyeStart')
    CurrentState = 'Goodbye'
    StateStartTime = time.time()
    
    if FacesDetectedCount > 1:
        StartAnim(random.choice(NextUpAnims))
    else:
        StartAnim(random.choice(GoodbyeAnims))
    
def GoodbyeUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        WaitLeaveStart()


def WaitLeaveStart():
    global StateStartTime
    global CurrentState
    global WaitTime
    
    print('WaitLeaveStart')
    CurrentState = 'WaitLeave'
    StateStartTime = time.time()
    WaitTime = time.time()
    
    StartAnim('Idle-Base')

def WaitLeaveUpdate():
    global StateStartTime
    bIsAnimFinished = UpdateAnim()
    
    # If the candy dispensor is triggered, deliver candy
    if CheckCandyTrigger() == True:
        TriggerCandyStart()
    
    # If we no longer see anyone, go back to idle
    elif CurrentClip == 'Idle-Base' and time.time() - LastFaceDetectTime > 2:
        IdleStart()
        
    # If people haven't left after brief time prompt to leave
    elif CurrentClip == 'Idle-Base' and time.time() - StateStartTime > 6:
        StartAnim(random.choice(GoAwayAnims))

    # If its been a long time, go back to idle
    elif CurrentClip == 'Idle-Base' and time.time() - WaitTime > 30:
        IdleStart()
        
    # If an animation has ended, start the idle anim
    elif bIsAnimFinished == True:
        StateStartTime = time.time()
        StartAnim('Idle-Base')


LoadAllAnims()

IdleStart()

#my_socket = socket.socket()

bExiting = False

while bExiting == False:
    try:
        print("Connecting...")
        #my_socket = socket.socket()
        #my_socket.connect(("boopi", port))
        
    except OSError:
        print("Failed to connect")
        my_socket.close()
        time.sleep(1)
        
    else:
        print("Connected!")

        while DISPLAY.loop_running() and bExiting == False:
            try:
                CurrentTime = time.time()
                
                # grab the frame from the threaded video stream and resize it
                # to 500px (to speedup processing)
                frame = vs.read()
                frame = imutils.resize(frame, width=ImageWidth)
                
                # Run Face Detection in another thread
                if DetectionDone == True:
                    for thread in threads:
                        thread.join()
                        
                    FacePos = []
                    FacesDetectedCount = len(FaceBoxes)
                    
                    for (top, right, bottom, left) in FaceBoxes:
                        #cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
                        FacePos = ((left + right) / 2.0, (top + bottom) / 2.0)
                        LastFaceDetectTime = CurrentTime
                        
                    if LastFaceDetectTime == CurrentTime:
                        FacesDetectedDuration += 1
                    else:
                        FacesDetectedDuration = 0

                    threads = []
                    DetectionDone = False
                    x = threading.Thread(target=run_detection, args=(frame,))
                    threads.append(x)
                    x.start()
                
                # Clear the skull rotation from last frame
                model_skull.rxryrz = (0, 0, 0)
                
                # Switch action based on the current state
                if ( CurrentState == 'Idle' ):
                    IdleUpdate()

                elif ( CurrentState == 'Greeting'):
                    GreetingUpdate()
                    
                elif ( CurrentState == 'Intro'):
                    IntroUpdate()
                    
                elif ( CurrentState == 'WaitTrigger'):
                    WaitTriggerUpdate()
                
                elif ( CurrentState == 'YourLoss'):
                    YourLossUpdate()

                elif ( CurrentState == 'TriggerCandy' ):
                    TriggerCandyUpdate()
                    
                elif ( CurrentState == 'Goodbye' ):
                    GoodbyeUpdate()
                    
                elif ( CurrentState == 'WaitLeave' ):
                    WaitLeaveUpdate()
                    
                elif ( CurrentState == 'ComeBack' ):
                    ComeBackUpdate()
                    
                elif ( CurrentState == 'Anyways' ):
                    AnywaysUpdate()
                    
                # Apply LookAt on top of 
                LookAtUser()
                
                # Render the Skull
                model_skull.draw()
                model_jaw.draw()
                
                k = mykeys.read()
                if k >-1:
                    if k==112:
                        pi3d.screenshot('skull_screenshot.jpg')
                    elif k==27:
                        bExiting = True
                        break
                    
            except BrokenPipeError:
                print("Disconnected")
                s.close()
                GPIO.output(ConnectionStatusPin, False)
                break;


# Cleanup
mykeys.close()
DISPLAY.destroy()
CurrentSound.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
