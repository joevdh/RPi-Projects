
import sys
sys.path.insert(0, '/home/pi/Projects/HexSpider/Code/Server')

from Control import *
from Servo import *
from tag_detector import TagDetector
from utils import *
from time import sleep
from vectormath import *
from pygame import *
from location import Location

ROBOT_TURN_INCREMENT = 14   # Max value that can be input to the system
REAL_TURN_INCREMENT = 48    # Max number of degrees the robot actually turns
TURN_SCALE = ROBOT_TURN_INCREMENT / REAL_TURN_INCREMENT

HEAD_YAW_MIN = -80
HEAD_YAW_MAX = 80
HEAD_PITCH_MIN = -40
HEAD_PITCH_MAX = 90

# Holds shared info about the current status
class SpiderInfo:
    def __init__(self, camera_info):
        self.control = Control("/home/pi/Projects/HexSpider/Code/Server/point.txt")
        self.servo = Servo()
        self.tagDetector = TagDetector(camera_info)
        self.tagLocation : Location = Location()
        self.headAngles : Vector2 = Vector2(0,-20)
        self.fTagLastSeenTime = 0.
        self.schedule = ()
        
        self.SetHeadAngles(self.headAngles)
        
    # Update the angles of the head
    def SetHeadAngles( self, newHeadAngles ):
        self.headAngles[0] = Clamp(newHeadAngles[0],HEAD_YAW_MIN,HEAD_YAW_MAX)
        self.headAngles[1] = Clamp(newHeadAngles[1],HEAD_PITCH_MIN,HEAD_PITCH_MAX)
        
        # convert to positive angles
        yaw = self.headAngles[0] + 90
        pitch = self.headAngles[1] + 90
        
        self.servo.setServoAngle(1, yaw)
        self.servo.setServoAngle(0, pitch)
        
    def TurnHead(self, delta : Vector2):
        self.SetHeadAngles( self.headAngles + delta)
        
    def TurnBody( self, angle ):
        #Move command:'CMD_MOVE'
        #Gait Mode: "1"
        #Moving direction: x='0',y='25'
        #Delay:'10'  Really its speed.  range 2-10
        #Action Mode : '0' = Angleless turn 

        while angle is not 0:
            
            angleDelta = Clamp(angle, -REAL_TURN_INCREMENT, REAL_TURN_INCREMENT )
            angle -= angleDelta
            
            print( "Angle: " + str(angle) + " Delta: " + str(angleDelta))
            
            data=['CMD_MOVE', '1', '0', '0', '10', angleDelta * TURN_SCALE ]
            self.control.run(data)
            
    def Walk( self, direction: Vector3, rotateAngle : float ):
        angleDelta = Clamp(rotateAngle, -REAL_TURN_INCREMENT, REAL_TURN_INCREMENT )
        data=['CMD_MOVE', '1', -direction.y, direction.x, '10', angleDelta * TURN_SCALE ]
        self.control.run(data)
        
    def UpdateTagLocation(self, tagPos):
        tagDist = tagPos[2]
        tagDir = AnglesToVector( Vector2( Rad2Deg( tagPos[0] ), Rad2Deg( tagPos[1] ) ) ).normalize()
        qHeadRot = AnglesToQuat(self.headAngles[0], self.headAngles[1])
        tagPosWS = qHeadRot.RotateVector(tagDir) * tagDist
        
        tagTransform = Transform(tagPosWS)
        self.tagLocation.Set( tagTransform )