import RPi.GPIO as GPIO
import time
import socket
from PCA9685 import PCA9685

MotorPin1 = 4
MotorPin2 = 14
PlungerServoIndex = 0
PlungerExtendAngle = 0
PlungerRetractAngle = 100

port = 10056
MaxConnections = 1

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set each pin to be either input or output
GPIO.setup(MotorPin1, GPIO.OUT)
GPIO.setup(MotorPin2, GPIO.OUT)

GPIO.output(MotorPin1, False)
GPIO.output(MotorPin2, False)

pwm = PCA9685(0x40)
pwm.setPWMFreq(50)

def FireCandy():
    GPIO.output(MotorPin1, True)
    GPIO.output(MotorPin2, True)
    time.sleep(.3)

    pwm.setServoAngle(PlungerServoIndex, PlungerExtendAngle)
    
    time.sleep(0.5)

    GPIO.output(MotorPin1, False)
    GPIO.output(MotorPin2, False)
    pwm.setServoAngle(PlungerServoIndex, PlungerRetractAngle)
    time.sleep(1)


print("Running...")


try:
    serversocket = socket.socket()
    
    try:
        serversocket.bind(('', port))
        
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    serversocket.listen(MaxConnections)

    while True:
            # accept connections from outside
            print('Listening...')
            (clientsocket, address) = serversocket.accept()
            print('Connected by', address)

            while True:
                try:
                    print('Waiting For Message...')
                    data = clientsocket.recv(1024).decode( "UTF-8" ) 
                except socket.error:
                    # Something else happened, handle error, exit, etc.
                    print("Error")
                    clientsocket.close()
                    break;
                except BrokenPipeError:
                    print("Disconnected")
                    clientsocket.close()
                    break;
                
                else:
                    if len(data) == 0:
                        print("Disconnect?")
                        break;
                    
                    print("Received: ", data)
                    if data == "Fire":
                        FireCandy()
    
except KeyboardInterrupt:
    print("Closing")
    GPIO.output(MotorPin1, False)
    GPIO.output(MotorPin2, False)
    pwm.setServoAngle(PlungerServoIndex, PlungerRetractAngle)
    serversocket.close()
    clientsocket.close()
    time.sleep(1)
   
