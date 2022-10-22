import RPi.GPIO as GPIO
from PiAnalog import *
import time
import socket


LightSensorOut = 18
LightSensorIn = 23
ProgramRunningPin = 4
ConnectionStatusPin = 14
port = 10056
LightOffResistance = 50000
msg = "gimme candy"
MinTimeBetweenShots = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set each pin to be either input or output
GPIO.setup(ProgramRunningPin, GPIO.OUT)
GPIO.setup(ConnectionStatusPin, GPIO.OUT)

p = PiAnalog(0.05, 1000)

GPIO.output(ConnectionStatusPin, False)
GPIO.output(ProgramRunningPin, False)

while True:
    try:
        print("Connecting...")
        s = socket.socket()
        s.connect(("boopi", port))
        
    except OSError:
        print("Failed to connect")
        s.close()
        time.sleep(1)
        
    else:
        print("Connected!")
        GPIO.output(ConnectionStatusPin, True)
        
        while True:
            try:
                # Wait until the light is on
                resistance = p.read_resistance()

                GPIO.output(ProgramRunningPin, False)

                #while resistance > LightOffResistance:
                 #   print(resistance)
                  #  print("Waiting for light...")
                   # time.sleep(0.1)
                    #resistance = p.read_resistance()
                    #continue

                #print("Ready to Shoot")

                resistance = p.read_resistance()
                if resistance > LightOffResistance:
                    GPIO.output(ProgramRunningPin, True)
                    print("Sending message:", msg)
                    s.sendall(msg.encode())
                    time.sleep(5)
                else:
                    GPIO.output(ProgramRunningPin, False)
                        
                
            except BrokenPipeError:
                print("Disconnected")
                s.close()
                GPIO.output(ConnectionStatusPin, False)
                break
        
            
    

