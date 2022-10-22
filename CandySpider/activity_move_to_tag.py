from spider_info import SpiderInfo
from activityid import ActivityID
from activity import Activity
from vectormath import *
from utils import *
from time import time as Time

THINK_INTERVAL = 0.2
GOAL_DISTANCE = 0.2
TAG_MISSING_TIMEOUT = 3
MOVE_SPEED = 35

class MoveToTag(Activity):
    def __init__(self, spiderInfo):
        print("Starting MoveToTag")
        Activity.__init__(self, spiderInfo)
        
    def Think(self, spiderInfo, data):
        
        # Is the detector ready to run
        if spiderInfo.tagDetector.IsReady():
            
            # Run detection
            bTagFound = spiderInfo.tagDetector.RunDetection(data)
            
            # If we found the tag we're done
            if bTagFound:
                tagPos = spiderInfo.tagDetector.detected_tags[0].pose_t
                
                # Update the head to look at the tag
                spiderInfo.TurnHead( Vector2( tagPos[0], tagPos[1] ) )
                
                spiderInfo.UpdateTagLocation(tagPos)
                
                
         # We lost sight of the tag, start searching again
        if ( Time() > spiderInfo.tagLocation.timeLastSeen + TAG_MISSING_TIMEOUT ):
            return ActivityID.FIND_TAG
        
        # If the distance to the tag is less than our target distance then step toward it
        distToTag = spiderInfo.tagLocation.transform.position.length()
        if ( distToTag > GOAL_DISTANCE ):
            moveVec = spiderInfo.tagLocation.transform.position
            moveVec = moveVec.normalize()
            angles = VectorToAngles(moveVec)
            
            print("MoveVec: " + str(moveVec))
            print("Angles: " + str(angles))
            
            spiderInfo.Walk(moveVec * MOVE_SPEED, angles[ANGLE.YAW])
            self.SetNextThink(THINK_INTERVAL)
            return ActivityID.CONTINUE
        else:
            print("Tag distance is " + str(distToTag) + ".  Exiting MoveToTag")
            return ActivityID.EXIT
        
        
       