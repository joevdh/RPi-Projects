import time
import sys
import struct
import socket
import threading

TRACKING_ADDRESS = "JoeSteamDeck"
TRACKING_PORT = 10056

class TrackerReceiver:
    def __init__(self):
        self._run = True
        self.listenThread = threading.Thread(target=self.ThreadFunc)
        self._position = []
        self._rotation = []
    
    def Stop(self):
        self._run = False
        self.listenThread.join()
    
    def ThreadFunc(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((TRACKING_ADDRESS, TRACKING_PORT))
            
        while self._run:
            
            # buffer size is 1024 bytes
            data, addr = sock.recvfrom(1024)
            print("Received message:", data)
            
            doubleCount = len(data) / 8
            trackingInfo = struct.unpack('d'*doubleCount, *data)
            
            self._position = trackingInfo[range(0,2)]
            self._rotation = trackingInfo[range(3,5)]
            
        sock.close()