
from activity import Activity, ActivityID
from spider_info import SpiderInfo
from utils import *
from activityid import ActivityID
from activity_findtag import FindTag
from activity_move_to_tag import MoveToTag
import time
import socket

# Network port to use when connecting to SteamVR tracker server
TRACKING_SERVER_ADDRESS = "JoeSteamDeck"
TRACKING_SERVER_PORT = 10056

def ActivityFactory(activityID, spiderInfo : SpiderInfo):
    activities = {
        ActivityID.FIND_TAG: FindTag,
        ActivityID.MOVE_TO_TAG: MoveToTag,
    }
 
    return activities[activityID](spiderInfo)


class CandySpider():

    def __init__(self, camera_info):
        self.spiderInfo = SpiderInfo(camera_info)
        self.activity : Activity = ActivityFactory(ActivityID.FIND_TAG, self.spiderInfo)
        self.trackerSocket : socket.socket = ()
        self.isTrackerConnected : bool = False
    
    def Shutdown(self):
        self.spiderInfo.control.relax(True)
        
    def write(self, data):
        
        # Try connecting first
        if self.isTrackerConnected == False:
            if self.TryConnect() == False:
                return
        
        # Once we no longer have an activity, we're done
        if self.activity is None:
            self.spiderInfo.control.relax(True)
            return
        
        # Otherwise, run the Think() function of the current activity after enough time
        # has passed
        if time() > self.activity.GetNextThink():
            newActivity = self.activity.Think(self.spiderInfo, data)
            
            if (newActivity == ActivityID.EXIT):
                self.activity = None
            
            elif (newActivity != ActivityID.CONTINUE):
                self.activity = ActivityFactory(newActivity, self.spiderInfo)
            
    def TryConnect(self) -> bool:
        try:
            print("Connecting...")
            self.trackerSocket = socket.socket()
            self.trackerSocket.connect((TRACKING_SERVER_ADDRESS, TRACKING_SERVER_PORT))
            
        except OSError:
            print("Failed to connect")
            self.trackerSocket.close()
            time.sleep(1)
            
        else:
            print("Connected!")
            self.isTrackerConnected = True
            return True