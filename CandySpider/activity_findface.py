from vectormath import *
from spider_info import SpiderInfo
from activityid import ActivityID
from activity import Activity

MIN_LOOK_ANGLE = -70
MAX_LOOK_ANGLE = 70
HEAD_TURN_INCREMENT = 25
BODY_TURN_INCREMENT = 90
LOOK_UP_ANGLE = 30
THINK_INTERVAL = 0.2

class FindFace(Activity):
    def __init__(self, spiderInfo):
        print("Starting FindTag")
        Activity.__init__(self, spiderInfo)
        startingHeadAngles = spiderInfo.headAngles
        startingHeadAngles[0] = MIN_LOOK_ANGLE
        startingHeadAngles[1] = LOOK_UP_ANGLE
        spiderInfo.SetHeadAngles(startingHeadAngles)
    
    def Think(self, spiderInfo, data):
        
        # Run detection
        bTagFound = spiderInfo.faceDetector.RunDetection(data)
        
        # If we found the tag we're done
        if bTagFound:
            # Update the location of the tag
            top, right, bottom, left = spiderInfo.faceDetector.detected_faces[0]
            
            # Start the activity to move towards the tag
            return ActivityID.MOVE_TO_TAG
        
        headAngles = spiderInfo.headAngles
        headAngles[0] += HEAD_TURN_INCREMENT
        
        # if we've looked through all the angles that the head can do, then turn the body and start over
        if headAngles[0] >= MAX_LOOK_ANGLE:
            headAngles[0] = MIN_LOOK_ANGLE
            spiderInfo.SetHeadAngles(headAngles)
            spiderInfo.TurnBody(BODY_TURN_INCREMENT)
            
        # Turn the head
        else:
            spiderInfo.SetHeadAngles(headAngles)
                
        self.SetNextThink(THINK_INTERVAL)
        
        return ActivityID.CONTINUE
