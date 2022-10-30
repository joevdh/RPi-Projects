import time
from spider_info import SpiderInfo
from location import Location
from vectormath import *
from utils import *

class StateManager:
    def __init__(self):
        self._currentState = None
        
    def Update( self, spiderInfo : SpiderInfo ):
        if self._currentState is None:
            return
        
        # Switch action based on the current state
        if ( self._currentState == 'WaitForFace' ):
            self.WaitForFace(spiderInfo)
        
        elif ( self._currentState == 'MoveToFace' ):
            self.MoveToFace(spiderInfo)
            
        elif ( self._currentState == 'PresentCandy' ):
            self.PresentCandy(spiderInfo)
            
        elif ( self._currentState == 'MoveToCaveEntrance' ):
            self.MoveToCaveEntrance(spiderInfo)
            
        elif ( self._currentState == 'BackIntoCave' ):
            self.BackIntoCave(spiderInfo)
            
    def MoveToFace( self, spiderInfo : SpiderInfo ):
        