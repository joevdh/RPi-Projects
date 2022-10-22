from __future__ import annotations
from vectormath import *
from time import time

class Location:
    def __init__(self):
        self._transform : Transform = Transform()
        self._timeLastSeen : float = 0.0
        
    @property
    def transform(self) -> Transform:
        return self._transform
    
    @property
    def timeLastSeen(self) -> Transform:
        return self._timeLastSeen
    
    def Set(self, newTransform: Transform):
        self._transform = newTransform
        self._timeLastSeen = time()