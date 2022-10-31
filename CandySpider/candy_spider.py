import sys
sys.path.insert(0, '/home/pi/RPi-Projects')

from Shared import *
from spider_info import SpiderInfo
from cameramanager import CameraManager
from movement_manager import MovementManager
import time
import pygame
import RPi.GPIO as GPIO

# Network port to use when connecting to SteamVR tracker server
TRACKING_SERVER_ADDRESS = "JoeSteamDeck"
TRACKING_SERVER_PORT = 10056

class CandySpider():

    def __init__(self):
        pygame.init()
        GPIO.setmode(GPIO.BCM)
        
        self.spiderInfo = SpiderInfo()
        self._camMgr : CameraManager = CameraManager()
        self._moveMgr : MovementManager = MovementManager()
        self._tracker : TrackerReceiver = TrackerReceiver()
    
    def Shutdown(self):
        self._camMgr.Stop()
        self._tracker.Stop()
        self._moveMgr.control.relax(True)
        GPIO.cleanup()
        
    def Update(self):
        
        self.spiderInfo.prevTime = self.spiderInfo.currTime
        self.spiderInfo.currTime = time.time()
        
        # Refresh readings from the sensors
        self.SyncLatestStatus()
        
        # Update the current state
        if self.spiderInfo.currentState is not None:
            self.spiderInfo.currentState.Update(self.spiderInfo)
        
        # # Look at a face
        # if self.spiderInfo.faceLocationsWS is not None and len(self.spiderInfo.faceLocationsWS) > 0:
        #     faceLoc : Location = self.spiderInfo.faceLocationsWS[0]
            
        #     if time.time() - faceLoc.timeStamp < 1:
        #         self.spiderInfo.LookAt(faceLoc.transform.position)
        #         self.spiderInfo.MoveTo(faceLoc.transform)
        #         print("MoveTo Face")
                
        #     elif self.spiderInfo.vTargetPos is None:
        #         targetTransform : Transform = Transform( Vector3(ParkStartPos), Quaternion.from_angle(180, (0,0,1)) )
        #         self.spiderInfo.LookAt(targetTransform.position)
        #         self.spiderInfo.MoveTo(targetTransform)
        #         print("MoveTo Home")
                
                
        self._moveMgr.Update(self.spiderInfo)

    # Read the most recent status from all the sensors and use it to
    # update our knowledge of the state of the world
    def SyncLatestStatus(self):
        # Update our position from the tracker
        if self._tracker.IsRunning():
            trackerXform = self._tracker.transform
            correctionQuat = Quaternion.from_angle(-90, (0, 1, 0))
            fixedQuat = trackerXform.rotation * correctionQuat
            
            self.spiderInfo.rootTransform = Transform(trackerXform.position, fixedQuat)
        
        # Update the world-space locations of the faces and tags.
        with self._camMgr.mutex:
            bCleared = False
            
            for faceLocationLS in self._camMgr.detected_faces:
                # If the sample is from a time when the head has stopped turning
                if faceLocationLS.timeStamp >= self._moveMgr.nextFaceReadyTime:
                    # if this is the first face, clear out the old list
                    if bCleared == False:
                        self.spiderInfo.faceLocationsWS = []
                        bCleared  = True
                    
                    print("MainThread time: " + str(time.time()))
                    headXformWS : Transform = self.spiderInfo.GetHeadTransformWS()
                    faceTransformWS = headXformWS * faceLocationLS.transform
                    self.spiderInfo.faceLocationsWS.append( Location(faceTransformWS, faceLocationLS.timeStamp) )
                    
        

if __name__ == '__main__':
    spider : CandySpider = CandySpider()
    
    try:
        while True:
            spider.Update()
            time.sleep(0.01)
    
    except Exception as e:
        print(e)
        
    finally:
        print("Stopping")
        spider.Shutdown()
