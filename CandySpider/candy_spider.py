import sys
sys.path.append('/home/pi/RPi-Projects/Shared')

from Shared import *
from spider_info import SpiderInfo
from cameramanager import CameraManager
from movement_manager import MovementManager
import time

# Network port to use when connecting to SteamVR tracker server
TRACKING_SERVER_ADDRESS = "JoeSteamDeck"
TRACKING_SERVER_PORT = 10056

CavePos = [0.256026, -0.157764, 0.0418488]
FrontRightCorner = [1.0302, -0.244911, 0.0475839]
FrontLeftCorner = [0.983952, 0.204809, 0.0481147]
ParkStartPos = [0.714544, -0.0587816, 0.0412334]
FrontEdgePos = [1.3426, 0.0333025, 0.0566583]


class CandySpider():

    def __init__(self):
        self.spiderInfo = SpiderInfo()
        #self.activity : Activity = ActivityFactory(ActivityID.FIND_FACE, self.spiderInfo)
        self._camMgr : CameraManager = CameraManager()
        self._moveMgr : MovementManager = MovementManager()
        self._tracker : TrackerReceiver = TrackerReceiver()
    
    def Shutdown(self):
        self._camMgr.Stop()
        self._tracker.Stop()
        self._moveMgr.control.relax(True)
        
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
        
        headXformWS : Transform = self.spiderInfo.GetHeadTransformWS()

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
