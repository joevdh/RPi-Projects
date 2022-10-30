import time
import sys
import struct
import socket
import threading
import queue

class MessageClient:
    def __init__(self, addr, port):
        self._run = True
        self._addr = addr
        self._port = port
        self._clientSocket = None
        self._messages : queue.Queue = queue.Queue()
        
        self._listenThread = threading.Thread(target=self.ThreadFunc)
        self._listenThread.start()
    
    def IsRunning(self):
        return self._run
    
    def Stop(self):
        self._run = False
        self._clientSocket.close()
        self._listenThread.join()

    def HasMessage(self):
        with self._mutex:
            return self._messages.empty() == False

    def GetMessage(self):
        with self._mutex:
            if self._messages.empty():
                return None
            else:
                return self._messages.get_nowait()

    def SendMessage(self, data):
        with self._mutex:
            self._clientSocket.sendall(data)
    
    def ThreadFunc(self): 
        while self._run:
            try:
                print("Connecting...")
                self._clientSocket = socket.socket()
                self._clientSocket.connect((self._addr, self._port))
                
            except OSError:
                print("Failed to connect")
                self._clientSocket.close()
                time.sleep(1)
                
            print("Connected!")

            while self._run:
                try:
                    data = self._clientSocket.recv(1024).decode( "UTF-8" )

                    if data is None or len(data) == 0:
                        print("Disconnect?")
                        break
                    
                    print("Received: ", data)
                    with self._mutex:
                        self._messages.put(data)

                except Exception as e:
                    print(e)
                    self._clientSocket.close()
                    break

        
if __name__ == '__main__':
    msgClient : MessageClient = MessageClient( "skully", 10057)
    
    try:
        while msgClient.IsRunning():
            msgServer.SendMessage("")

            while msgServer.HasMessage():
                msg = msgServer.GetMessage()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Exiting...")
        msgClient.Stop()