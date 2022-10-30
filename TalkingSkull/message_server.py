import time
import sys
import socket
import threading
import queue

#TRACKING_PORT = 10057

class MessageServer:
    def __init__(self, port):
        self._run = True
        self._clientSocket = None
        self._serversocket : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serversocket.settimeout(1)
        self._messages : queue.Queue = queue.Queue()
        self._mutex : threading.Lock = threading.Lock()
        
        try:
            self._serversocket.bind(('', port))
            self._serversocket.listen(1)
            
        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        
        self._listenThread = threading.Thread(target=self.ListenThreadFunc)
        self._listenThread.start()

    def Stop(self):
        print("Stopping")
        self._run = False
        self._serversocket.close()
        self._listenThread.join()
        print("Stopped")
    
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
        
    def ListenThreadFunc(self):
        print('Listening...')
        while self._run:
            try:
                (self._clientSocket, address) = self._serversocket.accept()
                
            except Exception as e:
                #print(e)
                continue

            while self._run:
                print('Connected by', address)

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
                    break
                        

if __name__ == '__main__':
    msgServer : MessageServer = MessageServer(10057)
    
    while True:
        try:
        
            while msgServer.HasMessage():
                msg = msgServer.GetMessage()
                msgServer.SendMessage(msg)

            time.sleep(1)
    
        except KeyboardInterrupt:
            print("Exiting...")
            msgServer.Stop()
            break
