import triad_openvr
import time
import sys
import struct
import socket
import threading

TRACKING_PORT = 10056
MAX_CONNECTIONS = 2
SAMPLE_INTERVAL = 1/250

class SenderServer:
    def __init__(self):
        self._run = True
        self._clientSockets = []
        self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listenThread = threading.Thread(target=self.ListenThreadFunc)
        self._mutex : threading.Lock = threading.Lock()
        
        try:
            self._serversocket.bind(('', TRACKING_PORT))
            self._serversocket.listen(MAX_CONNECTIONS)
            
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        
        self._listenThread.start()

    def Stop(self):
        self._run = False
        self._serversocket.close()
        self._listenThread.join()
    
    def SendToAll(self, data):
        with self._mutex:
            deleteList = []
            for client in self._clientSockets:
                if ( client is None ):
                    deleteList.append(client)
                else:
                    try:
                        client.sendall(data)
                    except:
                        client.close()
                        deleteList.append(client)
            
            for deadClient in deleteList:
                self._clientSockets.remove(deadClient)
        
    def ListenThreadFunc(self):
        print('Listening...')
        while self._run:
            try:
                (clientsocket, address) = self._serversocket.accept()
                print('Connected by', address)
            
                with self._mutex:
                    self._clientSockets.append(clientsocket)
                
            except Exception as e:
                print(e)
                self.Stop()
                
            
v = triad_openvr.triad_openvr()

serverMgr = SenderServer()

while True:
    try:
        start = time.time()

        data =  v.devices["tracker_1"].get_pose_quaternion()
        if data is None:
            print("Not Tracking Data")
            time.sleep(1)
        else:    
            sent = serverMgr.SendToAll(struct.pack('d'*len(data), *data))
        
            sleep_time = SAMPLE_INTERVAL - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
    except KeyError:
        print("Tracker Not Ready")
        v = None
        time.sleep(1)
        v = triad_openvr.triad_openvr()
        time.sleep(1)
                    
    except KeyboardInterrupt:
        print("Closing")
        serverMgr.Stop()
        time.sleep(1)
