import triad_openvr
import time
import sys
import struct
import socket

TRACKING_PORT = 10056
MAX_CONNECTIONS = 2

INTERVAL = 1/250

v = triad_openvr.triad_openvr()

try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    try:
        serversocket.bind(('', TRACKING_PORT))
        
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    serversocket.listen(MAX_CONNECTIONS)

    while True:
            # accept connections from outside
            print('Listening...')
            (clientsocket, address) = serversocket.accept()
            print('Connected by', address)

            while True:
                try:
                    start = time.time()

                    data =  v.devices["tracker_1"].get_pose_quaternion()
                    sent = clientsocket.sendall(struct.pack('d'*len(data), *data))
                    
                    sleep_time = INTERVAL-(time.time()-start)
                    if sleep_time>0:
                        time.sleep(sleep_time)
                    
                
                except KeyError:
                    print("Tracker Not Ready")
                    v = None
                    time.sleep(1)
                    v = triad_openvr.triad_openvr()
                    time.sleep(1)
                
                except socket.error:
                    # Something else happened, handle error, exit, etc.
                    print("Error")
                    clientsocket.close()
                    break
                
                except BrokenPipeError:
                    print("Disconnected")
                    clientsocket.close()
                    break
                
except KeyboardInterrupt:
    print("Closing")
    serversocket.close()
    clientsocket.close()
    time.sleep(1)
