import sys
sys.path.insert(0, '/home/pi/Projects/HexSpider/Code/Server')
sys.path.insert(0, '/home/pi/RPi-Projects')

from Control import *
from Servo import *
from Shared import *
from math import fabs
from token import NOTEQUAL
from spider_info import SpiderInfo
import time

ROBOT_TURN_INCREMENT = 14.0   # Max value that can be input to the system
REAL_TURN_INCREMENT = 48.0    # Max number of degrees the robot actually turns
TURN_SCALE = ROBOT_TURN_INCREMENT / REAL_TURN_INCREMENT

ROBOT_STEP_INCREMENT : float = 35.0
TARGET_POSITION_TOLERANCE = 0.15

HEAD_YAW_MIN = -80
HEAD_YAW_MAX = 80
HEAD_PITCH_MIN = -40
HEAD_PITCH_MAX = 90

HEAD_TURN_WAIT_TIME = 0.1

class MovementManager:
    def __init__(self):
        self.control = Control("/home/pi/Projects/HexSpider/Code/Server/point.txt")
        self.servo = Servo()

        self.nextFaceReadyTime : float = 0.0

        self._faceYaw : float = 0.0
        self._facePitch : float = 0.0


    def Update( self, settings : SpiderInfo ):
        vFaceDir = settings.headTransformLS.RotateVector( Vector3(1,0,0) )
        self.SetLookDirection(vFaceDir)
        
        vMoveVec : Vector3 = Vector3(0,0,0)
        flTurnDelta : float = 0.0
        
        if settings.flTargetYaw is not None:
            rootAngles : Vector2 = QuatToAngles(settings.rootTransform.rotation)
            flTurnDelta = AngleDiff( rootAngles[0], settings.flTargetYaw )
            #print("Target: " + str(settings.flTargetYaw) + " RootAngles: " + str(rootAngles) )
            #print("TurnAngle " + str(flTurnDelta))
            
        if settings.vTargetPos is not None and fabs(flTurnDelta) < 45:
            vToTarget : Vector3 = settings.vTargetPos - settings.rootTransform.position
            vToTarget.z = 0.0
            
            dist = vToTarget.length()
            #print("Distance: " + str(dist))
            if ( dist <= TARGET_POSITION_TOLERANCE ):
                settings.vTargetPos = None
            else:
                # Rotate into the spider's local space
                vMoveVec = settings.rootTransform.rotation.inverse().RotateVector(vToTarget.normalize())
                vMoveVec *= dist
                    
        if vMoveVec != Vector3(0,0,0) or flTurnDelta != 0:
            self.Move(vMoveVec, flTurnDelta)

        # if self._bMove is True:
        #     vMoveVec : Vector3 = self._vTargetMovePos - settings.rootTransform.position
        #     vMoveVec.z = 0.0
            
        #     dist = vMoveVec.length()
        #     #print("Distance: " + str(dist))
        #     if ( dist <= TARGET_POSITION_TOLERANCE ):
        #         self._bMove = False
        #         return
            
        #     # Rotate into the spider's local space
        #     vMoveVec = settings.rootTransform.rotation.inverse().RotateVector(vMoveVec.normalize())
        #     vMoveVec *= dist

        #     rootAngles : Vector2 = QuatToAngles(settings.rootTransform.rotation)
        #     flTurnDelta = AngleDiff( rootAngles[0], self._flTargetBodyYaw )
        #     #print("Target: " + str(self._flTargetBodyYaw) + " RootAngles: " + str(rootAngles) )
        #     #print("TurnAngle " + str(flTurnDelta))
        #     if fabs(flTurnDelta) > 45:
        #         vMoveVec = Vector3(0,0,0)
                
        #     self.Move(vMoveVec, flTurnDelta)

    # Set turn the head to look in the given direction
    def SetLookDirection( self, lookDir : Vector3 ):
        angles : Vector2 = VectorToAngles(lookDir)

        yaw = 0.0
        pitch = 0.0

        if IsBetween(angles[ANGLE.YAW], HEAD_YAW_MIN, HEAD_YAW_MAX) and IsBetween(angles[ANGLE.PITCH], HEAD_PITCH_MIN, HEAD_PITCH_MAX):
            yaw = angles[ANGLE.YAW]
            pitch = angles[ANGLE.PITCH]

        # convert to positive angles
        yaw += 90
        pitch += 90

        if CloseEnough(yaw, self._faceYaw) != True or CloseEnough(pitch, self._facePitch) != True:
            self._faceYaw = yaw
            self._facePitch = pitch
            self.servo.setServoAngle(1, yaw)
            self.servo.setServoAngle(0, pitch)
            self.nextFaceReadyTime = time.time() + HEAD_TURN_WAIT_TIME

    def Move( self, moveVec: Vector3, rotateAngle : float ):
        """
        Move the spider the given direction and distance

        Args:
            moveVec (Vector3): The relative direction and distance to move
            rotateAngle (float): The amount to turn.  Positive values are left, negative are right
        """
        #print("MoveVec " + str(moveVec.x) + ", " + str(moveVec.y))
        moveVec *= 100.0
        moveVec.x = Clamp(moveVec.x, -ROBOT_STEP_INCREMENT, ROBOT_STEP_INCREMENT)
        moveVec.y = Clamp(moveVec.y, -ROBOT_STEP_INCREMENT, ROBOT_STEP_INCREMENT)
        #print("MoveCmd " + str(moveVec.x) + ", " + str(moveVec.y))

        #Move command:'CMD_MOVE'
        #Gait Mode: "1"
        #Moving direction: x='0',y='25'
        #Delay:'10'  Really its speed.  range 2-10
        #Action Mode : '0' = Angleless turn
        angleDelta = Clamp(rotateAngle, -REAL_TURN_INCREMENT, REAL_TURN_INCREMENT ) * TURN_SCALE
        #print("TurnCmd: " + str(angleDelta))
        
        data=['CMD_MOVE', '1', -moveVec.y, moveVec.x, '10', -angleDelta ]
        self.control.run(data)