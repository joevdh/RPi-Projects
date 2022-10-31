from .utils import *
from pygame.math import Vector2
from pygame.math import Vector3
from .vectormath import *

def TestMath( result, expected ):
    if ( result != expected ):
        raise Exception("Test Failure.  Got " + str(result) + " expected " + str(expected))

testPairs = [
    [Vector3( 1, 0, 0), Vector2(0, 0)],
    [Vector3(-1, 0, 0), Vector2(180, 0)],
    [Vector3(0,1,0), Vector2(90, 0)],
    [Vector3(0,-1,0), Vector2(-90, 0)],
    [Vector3(0,0,1), Vector2(0, 90)],
    [Vector3(0,0,-1), Vector2(0, -90)],
    [Vector3(0.7, 0.7, 0).normalize(), Vector2(45, 0)],
    [Vector3(0.7, -0.7, 0).normalize(), Vector2(-45, 0)],
    [Vector3(0.7, 0, 0.7).normalize(), Vector2(0, 45)],
    [Vector3(0.7, 0, -0.7).normalize(), Vector2(0, -45)],
 ]

for x in testPairs:
    TestMath(VectorToAngles(x[0]), x[1])
    TestMath(AnglesToVector(x[1]), x[0])

for testPair in testPairs:
    rot = AnglesToQuat( testPair[1] )
    testVec = rot.RotateVector( Vector3(1,0,0) )
    print( str(testPair[1]) + " -> " + str(testVec) )
    TestMath(testVec, testPair[0] )
    
x1 = Transform()
x2 = Transform()
x3 = x1 * x2
    
print("Tests succeeded")
