import pygame
import time

pygame.init() 
CurrentSound : pygame.mixer.Sound= pygame.mixer.Sound('/home/pi/RPi-Projects/TalkingSkull/resources/clips/Anyways1.wav')

CurrentSound.play(loops=0)
print("Playng")

length = CurrentSound.get_length()
     
time.sleep(length)

print("Done")
