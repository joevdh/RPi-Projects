#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Wavefront obj model loading. Material properties set in mtl file.
Uses the import pi3d method to load *everything*
"""

import sys
sys.path.insert(0, '/home/pi/RPi-Projects')

from Shared import *
import pi3d
import RPi.GPIO as GPIO
import csv
import time
import pygame
from imutils.video import VideoStream
import face_recognition
import imutils
import time
import cv2
import threading
import random


# Global Constants
spider_port = 10057

MovementScale = 2.54
ModelScale = 0.005
ImageWidth = 500
ImageHeight = 500

LookAtCenterX = 500 / 2
LookAtCenterY = 375 / 2
LookAtPitchScale = 10
LookAtYawScale = 10
LookAtSpeedScale = 0.2

FacesDetectedCount = 0
FacesDetectedDuration = 0
LastFaceDetectTime = time.time()
LastFaceDetectedTimeOut = 2

FrameRate = 30
TimeStep = 1.0 / FrameRate

TriggerDistance = 50
TriggerCount = 0

IdleAnims = [ '00_Idle-Base' ]
GreetingAnims = [ '01_Greeting1', '01_Greeting2', '01_Greeting3', '01_HelloToYou' ]
IntroAnims = [ '02_HereForCandy' ]
WakeUpAnims = [ '03_WakeBug1', '03_WakeBug2' ]
GoDeliverAnims = [ '04_GoDeliver1', '04_GoDeliver2', '04_GoDeliver3' ]
TakeCandyPromptAnims = [ '05_TakePrompt1', '05_TakePrompt2', '05_TakePrompt3' ]
AnyoneElseAnims = [ '06_AnyoneElse1', '06_AnyoneElse2', '06_AnyoneElse3' ]
OnTakeAnims = [ '07_OnTake1', '07_OnTake2', '07_OnTake3' ]
HangOnAnims = [ '08_HangOn1', '08_HangOn2' ]
GoHomeAnims = [ '09_GoHome1', '09_GoHome2' ]
GoodbyeAnims = [ '10_Goodbye1', '10_Goodbye2', '10_Goodbye3', '10_End1', '10_End2', '10_End3', '10_End4']

# Global Variables
AnimList = {}
CurrentClip = ''
CurrentAnimData = []
CurrentSound = 0
nFrameIndex = 0
CurrentState = 'Idle'
StateStartTime = 0
WaitTime = 0
SpiderStatus = 'Idle'
BowlStatus = 'Clear'    # or 'Occupied'
SpiderPos : Vector3 = Vector3(0,0,0)

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

msgServer : MessageServer = MessageServer(spider_port)

pygame.init()

CurrentSound = pygame.mixer.Sound('resources/2022/00_Idle-Base.wav')

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
#vs = VideoStream(src=0,framerate=1).start()
vs = VideoStream(usePiCamera=True).start()
#time.sleep(2.0)

# Setup display and initialise pi3d
#DISPLAY = pi3d.Display.create(x=100, y=100, background=(0, 0, 0, 1), frames_per_second=FrameRate)
DISPLAY = pi3d.Display.create(background=(0, 0, 0, 1), frames_per_second=FrameRate)
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

def run_detection(frame):
    global FaceBoxes
    global DetectionDone
    FaceBoxes = face_recognition.face_locations(frame)
    DetectionDone = True

def LoadAnim(clipName):
    global AnimList
    
    print('Loading ' + clipName)
    
    animData = []
    with open('resources/2022/' + clipName + '.csv') as csvfile:
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
        
    clip = pygame.mixer.Sound('resources/2022/' + clipName + '.wav')
    
    AnimList[clipName] = [ animData, clip ]

def LoadAllAnims():
    for clipName in IdleAnims:
        LoadAnim(clipName)

    for clipName in GreetingAnims:
        LoadAnim(clipName)

    for clipName in IntroAnims:
        LoadAnim(clipName)

    for clipName in WakeUpAnims:
        LoadAnim(clipName)

    for clipName in GoDeliverAnims:
        LoadAnim(clipName)

    for clipName in TakeCandyPromptAnims:
        LoadAnim(clipName)

    for clipName in AnyoneElseAnims:
        LoadAnim(clipName)

    for clipName in OnTakeAnims:
        LoadAnim(clipName)

    for clipName in HangOnAnims:
        LoadAnim(clipName)

    for clipName in GoHomeAnims:
        LoadAnim(clipName)

    for clipName in GoodbyeAnims:
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
    StartAnim(IdleAnims[0])
    
def IdleUpdate():
    global StateStartTime
    
    # If we detected a face, go to Greeting
    if FacesDetectedDuration >= 1:
        GreetingStart()

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
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IntroStart()


def IntroStart():
    global StateStartTime
    global CurrentState
    
    print('IntroStart')
    CurrentState = 'Intro'
    StateStartTime = time.time()
    StartAnim(random.choice(IntroAnims))
     
def IntroUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        WakeUpStart()


def WakeUpStart():
    global StateStartTime
    global CurrentState
    
    
    print('WakeUpStart')
    CurrentState = 'WakeUp'
    StateStartTime = time.time()
    StartAnim(random.choice(WakeUpAnims))

def WakeUpUpdate():
    global msgServer

    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        msgServer.SendMessage(SpiderCommand.WAKEUP)
        
def WakeUpWaitStart():
    global StateStartTime
    global CurrentState
    global msgServer
    
    print('WakeUpWaitStart')
    CurrentState = 'WakeUpWait'
    StateStartTime = time.time()
    StartAnim(random.choice(IdleAnims))

def WakeUpWaitUpdate():
    if SpiderStatus == SpiderStatus.AWAKE:
        DeliverStart()

def DeliverStart():
    global StateStartTime
    global CurrentState
    
    print('DeliverStart')
    CurrentState = 'Deliver'
    StateStartTime = time.time()
    StartAnim(random.choice(GoDeliverAnims))
    msgServer.SendMessage("Deliver")

def DeliverUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True and SpiderStatus == "DeliveryReady":
        TakePromptStart()

def TakePromptStart():
    global StateStartTime
    global CurrentState
    
    print('TakePrompt')
    CurrentState = 'TakePrompt'
    StateStartTime = time.time()
    StartAnim(random.choice(TakeCandyPromptAnims))

def TakePromptUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True or SpiderStatus == "CandyGrabDetected":
        OnTakeStart()

def OnTakeStart():
    global StateStartTime
    global CurrentState
    
    print('OnTake')
    CurrentState = 'OnTake'
    StateStartTime = time.time()
    StartAnim(random.choice(OnTakeAnims))

def OnTakeUpdate():
    bIsAnimFinished = UpdateAnim()
    elapsedTime = time.time() - StateStartTime
    if (bIsAnimFinished == True and SpiderStatus == "Idle") or elapsedTime > 20.0:
        AnyoneElseStart()

def AnyoneElseStart():
    global StateStartTime
    global CurrentState
    
    print('AnyoneElse')
    CurrentState = 'AnyoneElse'
    StateStartTime = time.time()
    StartAnim(random.choice(AnyoneElseAnims))

def AnyoneElseUpdate():
    bIsAnimFinished = UpdateAnim()
    elapsedTime = time.time() - StateStartTime
    if bIsAnimFinished == True and elapsedTime > 10.0:
        GoHomeStart()

def GoHomeStart():
    global StateStartTime
    global CurrentState
    
    print('GoHome')
    CurrentState = 'GoHome'
    StateStartTime = time.time()
    StartAnim(random.choice(GoHomeAnims))
    msgServer.SendMessage("GoHome")

def GoHomeUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True and SpiderStatus == "HomeAwake":
        GoodbyeStart()

def GoodbyeStart():
    global StateStartTime
    global CurrentState
    
    print('GoodbyeStart')
    CurrentState = 'Goodbye'
    StateStartTime = time.time()
    
    StartAnim(random.choice(GoodbyeAnims))
    msgServer.SendMessage("Sleep")

    # if FacesDetectedCount > 1:
    #     StartAnim(random.choice(NextUpAnims))
    # else:
    #     StartAnim(random.choice(GoodbyeAnims))
    
def GoodbyeUpdate():
    bIsAnimFinished = UpdateAnim()
    if bIsAnimFinished == True:
        IdleStart()



LoadAllAnims()

IdleStart()

bExiting = False


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

        # Update the status of the spider
        while msgServer.HasMessage():
            ( category, data ) = msgServer.GetMessage().split(":", 1)
            print("Received Spider Message: " + str(category) + " " + str(data))
            
            if category is 'Spider':
                SpiderStatus = data
            elif category is 'Bowl':
                BowlStatus = data
            elif category is 'Position':
                pos = data.split(",")
                SpiderPos = Vector3(pos[0], pos[1], pos[2])
        
        # Switch action based on the current state
        if ( CurrentState == 'Idle' ):
            IdleUpdate()

        elif ( CurrentState == 'Greeting'):
            GreetingUpdate()
            
        elif ( CurrentState == 'Intro' ):
            IntroUpdate()

        elif ( CurrentState == 'WakeUp' ):
            WakeUpUpdate()

        elif ( CurrentState == 'Deliver' ):
            DeliverUpdate()

        elif ( CurrentState == 'TakePrompt' ):
            TakePromptUpdate()

        elif ( CurrentState == 'AnyoneElse' ):
            AnyoneElseUpdate()

        elif ( CurrentState == 'OnTake' ):
            OnTakeUpdate()

        elif ( CurrentState == 'GoHome' ):
            GoHomeUpdate()
            
        elif ( CurrentState == 'Goodbye' ):
            GoodbyeUpdate()
            
        # Apply LookAt on top of the current anim
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

    except KeyboardInterrupt:
        break

    except Exception as e:
        print(e)
        break
            
# Cleanup
msgServer.Stop()
mykeys.close()
DISPLAY.destroy()
CurrentSound.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
