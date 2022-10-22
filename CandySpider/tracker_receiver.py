import time
import sys
import struct
import socket
import threading
from vectormath import *

TRACKING_ADDRESS = "JoeSteamDeck"
TRACKING_PORT = 10056

# Function to print out text but instead of starting a new line it will overwrite the existing line
def update_text(txt):
    sys.stdout.write('\r'+txt)
    sys.stdout.flush()

class TrackerReceiver:
    def __init__(self):
        self._run = True
        self.listenThread = threading.Thread(target=self.ThreadFunc)
        self._transform : Transform = ()
        
        self.listenThread.start()
    
    def IsRunning(self):
        return self._run
    
    def Stop(self):
        self._run = False
        self.listenThread.join()
    
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
                        
                        self._transform.position = Vector3( trackingInfo[0], trackingInfo[1], trackingInfo[2] )
                        self._transform.rotation = Quaternion( trackingInfo[3], trackingInfo[4], trackingInfo[5], trackingInfo[6] )
                        update_text( str(self._transform) )
                        
                    except BrokenPipeError:
                        print("Disconnected")
                        sock.close()
                        break
                    except:
                        self._run = False
                        sock.close()
                        break
            
        sock.close()
        
if __name__ == '__main__':
    tracker=TrackerReceiver()
    
    try:
        while tracker.IsRunning():
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("Exiting...")
        tracker.Stop()