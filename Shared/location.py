from __future__ import annotations
from .vectormath import *
from time import time

class Location:
    def __init__(self, xform = Transform(), timeStamp = 0.0 ):
        self._transform : Transform = xform
        self._timeStamp : float = timeStamp
        
    @property
    def transform(self) -> Transform:
        return self._transform
    
    @property
    def timeStamp(self) -> Transform:
        return self._timeStamp
    
    def Set(self, newTransform: Transform):
        self._transform = newTransform
        self._timeStamp = time()