import RPi.GPIO as GPIO
import time

ledPin= 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin , GPIO.IN)

while True:
  try:
    if GPIO.input(ledPin):
      print("On")
    else:
      print("Off")
    time.sleep(0.05)
    
  except KeyboardInterrupt:
    break
  
  
GPIO.cleanup()
