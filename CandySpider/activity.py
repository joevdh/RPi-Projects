from time import time as Time
from activityid import ActivityID
from abc import abstractmethod
from spider_info import SpiderInfo

class Activity:
    def __init__(self, spiderInfo):
        self._nextThinkTime = 0
        
    def GetNextThink(self):
        return self._nextThinkTime
    
    def SetNextThink(self, timeIncrement):
        self._nextThinkTime = Time() + timeIncrement
    
    @abstractmethod
    def Think(self, spiderInfo : SpiderInfo, data) -> ActivityID:
        pass
