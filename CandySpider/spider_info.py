from utils import *
from time import sleep
from vectormath import *
from pygame import *
from location import Location

# Holds shared info about the current status
class SpiderInfo:
    def __init__(self):
        self.schedule = ()
        
        self.rootTransform : Transform = Transform()
        self.headTransformLS : Transform = Transform(Vector3(0.12,0,0))
        
        self.currTime = 0.0
        self.prevTime = 0.0
        
        self.tagLocations = []
        self.faceLocationsWS = []
        
        self.vTargetPos = None
        self.flTargetYaw  = None
    
    def GetHeadTransformWS(self) -> Transform:
        return self.rootTransform * self.headTransformLS
    
    def LookAt(self, vLookTargetWS : Vector3):
        """
        Turn the head to look at the given target location

        Args:
            vLookTargetWS (Vector3): The 3D position of the look target, in world space
        """
        
        vLookTargetMS = self.rootTransform.Inverse().TransformVector(vLookTargetWS)
        vToLookTarget = vLookTargetMS - self.headTransformLS.position
        angles = VectorToAngles(vToLookTarget.normalize())
        self.headTransformLS = Transform( self.headTransformLS.position, AnglesToQuat(angles) )
        
    def MoveTo( self, targetXform : Transform ):
        self.vTargetPos = targetXform.position
        self.flTargetYaw = QuatToAngles(targetXform.rotation)[0]
    
    def UpdateTagLocation(self, tagPos):
        tagDist = tagPos[2]
        tagDir = AnglesToVector( Vector2( Rad2Deg( tagPos[0] ), Rad2Deg( tagPos[1] ) ) ).normalize()
        qHeadRot = AnglesToQuat(self.headAngles[0], self.headAngles[1])
        tagPosWS = qHeadRot.RotateVector(tagDir) * tagDist
        
        tagTransform = Transform(tagPosWS)
        self.tagLocation.Set( tagTransform )