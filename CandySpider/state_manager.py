import time
from abc import abstractmethod
from spider_info import SpiderInfo
from location import Location
from vectormath import *
from utils import *

###################################################
class StateID:
    SLEEPING = "SLEEPING"
    WAKEUP = "WAKEUP"
    AWAKE = "AWAKE"
    WALKOUT = "WALKOUT"
    PRESENTCANDY = "PRESENTCANDY"
    WALKHOME = "WALKHOME"
    
    def __init__(self):
        pass

###################################################
def StateFactory(stateID, spiderInfo : SpiderInfo):
    states = {
        StateID.SLEEPING: Sleeping,
        StateID.WAKEUP: WakeUp,
        StateID.AWAKE: MoveToTag,
    }
 
    return states[stateID](spiderInfo)

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
        
        headRot = AnglesToQuat(Vector2(0.0, -50.0))
        spiderInfo.headTransformLS = Transform(spiderInfo.headTransformLS.position, headRot)

    def Update(self, spiderInfo : SpiderInfo):
        if spiderInfo.messageMgr.HasMessage():
            if spiderInfo.messageMgr.GetMessage() == "WakeUp":
                spiderInfo.currentState = WakeUp(spiderInfo)
            
###################################################
class WakeUp(State):
    def __init__(self, spiderInfo : SpiderInfo):
        State.__init__(self, spiderInfo)
        
    def Update(self, spiderInfo : SpiderInfo):
        pass

