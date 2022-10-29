from __future__ import annotations
from vectormath import Quaternion
from pygame import Vector3


__all__ = ['Transform']

class Transform():
    
    def __new__(cls, pos: Vector3 = Vector3(0.0, 0.0, 0.0), rot: Quaternion = Quaternion(1.0, 0.0, 0.0, 0.0) ):
        self = object.__new__(cls)
        self._position: Vector3 = pos
        self._rotation: Quaternion = rot
        return self
    
    @property
    def position(self) -> Vector3:
        return self._position
    
    @property
    def rotation(self) -> Quaternion:
        return self._rotation
    
    def __str__(self) -> str:
        posStr = "Position: " + str( self._position )
        rotStr = "Rotation: " + str( self._rotation )
        return str(posStr + " " + rotStr)
    
    def __mul__(self, other: Transform) -> Transform:
        newQuat : Quaternion = self.rotation * other.rotation
        newPos = self.position + self.rotation.RotateVector(other.position)
        return Transform(newPos, newQuat)
    
    def Inverse(self) -> Transform:
        outRot : Quaternion = self.rotation.conjugate()
        outPos : Vector3 = outRot.RotateVector(self.position) * -1.0
        return Transform(outPos, outRot)
    
    def TransformVector(self, vector: Vector3) -> Vector3:
        return self._position + self._rotation.RotateVector(vector)
    
    def RotateVector(self, vector: Vector3) -> Vector3:
        return self._rotation.RotateVector(vector)
    
    