import time
import sys
import struct
import socket
import threading
from vectormath import *
from utils import *

TRACKING_ADDRESS = "JoeSteamDeck"
TRACKING_PORT = 10056

class TrackerReceiver:
    def __init__(self):
        self._run = True
        self.listenThread = threading.Thread(target=self.ThreadFunc)
        self._transform : Transform = Transform()
        
        self.listenThread.start()
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    def IsRunning(self):
        return self._run
    
    def Stop(self):
        print("Tracker Stopping")
        self._run = False
        self.listenThread.join()
        print("Tracker Stopped")
    
    def ThreadFunc(self): 
        while self._run:
            try:
                print("Connecting...")
                sock = socket.socket()
                sock.connect((TRACKING_ADDRESS, TRACKING_PORT))
                
            except OSError:
                print("Failed to connect")
                sock.close()
                time.sleep(1)
                
            else:
                print("Connected!")

                while self._run:
                    try:
                        # Blocking call.  Buffer size is 1024 bytes
                        data = sock.recv(1024)
                        
                        if not data:
                            print("Disconnected")
                            sock.close()
                            break
                        
                        doubleCount = int(len(data) / 8)
                        trackingInfo = struct.unpack('d'*doubleCount, data)
                        
                        if len(trackingInfo) is 7:
                            # OpenVR
                            # right-handed system 
                            # +y is up 
                            # +x is to the right 
                            # -z is forward 
                            # Distance unit is  meters 
                            
                            # Spider
                            # +z is up
                            # -y is right
                            # +x is forward
                            
                            newPos = Vector3( -trackingInfo[2], -trackingInfo[0], trackingInfo[1] )
                            newRot = Quaternion( trackingInfo[3], -trackingInfo[6], -trackingInfo[4], trackingInfo[5] )
                            self._transform = Transform(newPos, newRot)
                            #update_text( str(self._transform) )
                        
                    except BrokenPipeError:
                        print("Disconnected")
                        sock.close()
                        break
                    
                    except Exception as e:
                        print("Tracker Thread: " + str(e))
                        self._run = False
                        sock.close()
                        break
            
        sock.close()
        
if __name__ == '__main__':
    tracker=TrackerReceiver()
    
    try:
        while tracker.IsRunning():
            update_text( str(tracker.transform) )
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("Exiting...")
        tracker.Stop()