import time
from abc import abstractmethod
from Shared.net_messages import MakeSpiderStatusMessage
from spider_info import SpiderInfo
from Shared import *
import pygame
import RPi.GPIO as GPIO

SLEEP_HEAD_ANGLE = -50
YAWN_HEAD_ANGLE = 50

BOWL_DETECTION_PIN= 16

CavePos = Vector3(0.256026, -0.157764, 0.0418488)
FrontRightCorner = Vector3(1.0302, -0.244911, 0.0475839)
FrontLeftCorner = Vector3(0.983952, 0.204809, 0.0481147)
ParkStartPos = Vector3(0.714544, -0.0587816, 0.0412334)
FrontEdgePos = Vector3(1.3426, 0.0333025, 0.0566583)

###################################################
class State:
    """
    Base Class for states
    """
    def __init__(self, spiderInfo : SpiderInfo):
        self.startTime = spiderInfo.currTime
    
    @abstractmethod
    def Update(self, spiderInfo : SpiderInfo):
        pass


###################################################
class Sleeping(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.bRelax = True
        
        # Look down
        headRot = AnglesToQuat(Vector2(0.0, -50.0))
        spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, headRot)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.SLEEPING) )

    def Update(self, spiderInfo : SpiderInfo):
        if spiderInfo.messageMgr.HasMessage():
            if spiderInfo.messageMgr.GetMessage() == SpiderCommand.WAKEUP:
                spiderInfo.currentState = WakeUp(spiderInfo)
            
            
###################################################
class WakeUp(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        # play the yawning sounds
        self.currentSound : pygame.mixer.Sound = pygame.mixer.Sound('/home/pi/RPi-Projects/CandySpider/resources/Yawn.wav')
        self.soundLength = self.currentSound.get_length()
        
    def Update(self, spiderInfo : SpiderInfo):
        elapsedTime = spiderInfo.currTime - self.startTime
        
        if elapsedTime > self.soundLength:
            spiderInfo.currentState = Awake(spiderInfo)
        
        elif elapsedTime > (self.soundLength / 2.0):
            # animate down
            halfSoundLength = self.soundLength / 2.0
            lerpVal = (elapsedTime - halfSoundLength) / halfSoundLength
            headAngle = Lerp(YAWN_HEAD_ANGLE, 0.0, lerpVal)
            headRot = AnglesToQuat(Vector2(0.0, headAngle))
            spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, headRot)
        
        else:
            # animate up
            lerpVal = elapsedTime / (self.soundLength / 2.0)
            headAngle = Lerp(SLEEP_HEAD_ANGLE, YAWN_HEAD_ANGLE, lerpVal)
            headRot = AnglesToQuat(Vector2(0.0, headAngle))
            spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, headRot)


###################################################
class Awake(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.AWAKE) )
        
    def Update(self, spiderInfo : SpiderInfo):
        # wait for message
        if spiderInfo.messageMgr.HasMessage():
            msg = spiderInfo.messageMgr.GetMessage()
            
            if msg == SpiderCommand.SLEEP:
                spiderInfo.currentState = Sleeping(spiderInfo)
                
            elif msg == SpiderCommand.ASK_CANDY:
                spiderInfo.currentState = CandyQuestion(spiderInfo)
                
                
###################################################
class CandyQuestion(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.CANDY_QUESTION) )
        
        self.currentSound : pygame.mixer.Sound = pygame.mixer.Sound('/home/pi/RPi-Projects/CandySpider/resources/Candy_Question.wav')
        self.soundLength = self.currentSound.get_length()
        
        spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, AnglesToQuat(Vector2(0.0, 70)))
        
    def Update(self, spiderInfo : SpiderInfo):
        if spiderInfo.messageMgr.HasMessage():
            if spiderInfo.messageMgr.GetMessage() == SpiderCommand.DELIVER_CANDY:
                spiderInfo.currentState = DeliverCandy(spiderInfo)
            
            
###################################################
class DeliverCandy(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.DELIVERING_CANDY) )
        
        # If we detect a face look at it
        bLookingAtFace = False
        if len(spiderInfo.faceLocationsWS) > 0:
            faceLoc : Location = spiderInfo.faceLocationsWS[0]
            
            if time.time() - faceLoc.timeStamp < 1:
                spiderInfo.LookAt(faceLoc.transform.position)
                bLookingAtFace = True
        
        # If no face is detected just look straight ahead
        if bLookingAtFace == False:
            spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, AnglesToQuat(Vector2(0.0, 0.0)))
        
        self.currentSound : pygame.mixer.Sound = pygame.mixer.Sound('/home/pi/RPi-Projects/CandySpider/resources/Deliver.wav')
        self.soundLength = self.currentSound.get_length()
        
        spiderInfo.MoveTo( Transform(FrontEdgePos) )
        
    def Update(self, spiderInfo : SpiderInfo):
        # Wait until the spider gets in position
        if spiderInfo.vTargetPos is None:
            spiderInfo.currentState = PresentCandy(spiderInfo)


###################################################       
class PresentCandy(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.PRESENTING_CANDY) )
        
        GPIO.setup(BOWL_DETECTION_PIN , GPIO.IN)
        
    def Update(self, spiderInfo : SpiderInfo):
        if GPIO.input(BOWL_DETECTION_PIN):
            spiderInfo.messageMgr.SendMessage( MakeBowlStatusMessage(BowlStatus.OCCUPIED) )
            
        else:
            spiderInfo.messageMgr.SendMessage( MakeBowlStatusMessage(BowlStatus.UNOCCUPIED) )
            
        if spiderInfo.messageMgr.HasMessage():
            if spiderInfo.messageMgr.GetMessage() == SpiderCommand.GO_HOME:
                spiderInfo.messageMgr.SendMessage( MakeBowlStatusMessage(BowlStatus.UNOCCUPIED) )
                spiderInfo.currentState = GoingHome(spiderInfo)
                
                
###################################################       
class GoingHome(State):
    WALK_TO_ENTRY = "WALK_TO_ENTRY"
    TURN_AROUND = "TURN_AROUND"
    BACK_IN = "BACK_IN"
    
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
        spiderInfo.messageMgr.SendMessage( MakeSpiderStatusMessage(SpiderStatus.WALKING_HOME) )
        
        spiderInfo.MoveTo(ParkStartPos)
        
        self.stage = self.WALK_TO_ENTRY
        
    def Update(self, spiderInfo : SpiderInfo):
        if self.stage == self.WALK_TO_ENTRY:
            if spiderInfo.vTargetPos is None:
                self.stage = self.TURN_AROUND
                spiderInfo.MoveTo( Transform(spiderInfo.rootTransform.position) )
                
        elif self.stage == self.TURN_AROUND:
            if spiderInfo.flTargetYaw is None:
                self.stage = self.BACK_IN
                spiderInfo.MoveTo( Transform(CavePos) )
                
        if self.stage == self.BACK_IN:
            if spiderInfo.vTargetPos is None:
                spiderInfo.currentState = Sleeping(spiderInfo)
                