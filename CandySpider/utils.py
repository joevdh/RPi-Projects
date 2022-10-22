
import math
from pygame.math import Vector2
from pygame.math import Vector3
from vectormath import *

class AXIS:
    FORWARD = 0
    LEFT = 1
    UP = 2
    def __init__(self):
        pass
    
class ANGLE:
    YAW = 0
    PITCH = 1
    ROLL = 2
    def __init__(self):
        pass

def Sqr( x ):
    return x * x

def Rad2Deg( angleRadians ):
    return angleRadians * 180. / math.pi

def Deg2Rad( angleDegrees ):
    return angleDegrees * math.pi / 180.

def Clamp(value, minValue, maxValue):
    if value < minValue:
        return minValue
    elif value > maxValue:
        return maxValue
    else:
        return value

def VectorToAngles( vForward : Vector3 ) -> Vector2:
    yaw = 0.0
    pitch = 0.0

    if ( vForward[AXIS.LEFT] == 0.0 and vForward[AXIS.FORWARD] == 0.0 ):
        yaw = 0.0
        if ( vForward[AXIS.UP] > 0.0 ):
            pitch = 90.0
        else:
            pitch = -90.0
    
    else:
        yaw = Rad2Deg( math.atan2(vForward[AXIS.LEFT], vForward[AXIS.FORWARD]) )
        
        tmp = math.sqrt( Sqr(vForward[AXIS.FORWARD]) + Sqr(vForward[AXIS.LEFT]) )
        pitch = Rad2Deg( math.atan2(vForward[AXIS.UP], tmp) )

    return Vector2( yaw, pitch )

def AnglesToVector( angles : Vector2 ) -> Vector3:
    yawSin = math.sin( Deg2Rad( angles[ANGLE.YAW] ) )
    yawCos = math.cos( Deg2Rad( angles[ANGLE.YAW] ) )
    
    pitchSin = math.sin( Deg2Rad( angles[ANGLE.PITCH] ) )
    pitchCos = math.cos( Deg2Rad( angles[ANGLE.PITCH] ) )
    
    return Vector3( pitchCos * yawCos, pitchCos * yawSin, pitchSin )

def AnglesToQuat(yaw : float, pitch : float) -> Quaternion:
        yawRot = Quaternion.from_angle(yaw, (0,0,1))
        pitchRot = Quaternion.from_angle(pitch, (0,1,0))
        return yawRot * pitchRot

def ToSpiderCoords( coordsIn : Vector3 ) -> Vector3:
    # Code coords: x = forward, y = left, z = up
    # Spider coords: x = right, y = up, z = forward
    return Vector3(-coordsIn.y, coordsIn.z, coordsIn.x)
