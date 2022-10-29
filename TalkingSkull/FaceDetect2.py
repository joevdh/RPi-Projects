from imutils.video import VideoStream
import face_recognition
import imutils
import time
import numpy as np
import cv2

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
#vs = VideoStream(src=0,framerate=1).start()
vs = VideoStream(usePiCamera=True, resolution=(320, 240), framerate=32).start()
time.sleep(2.0)

print("Starting")

def hisEqulColor(img):
    ycrcb=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    channels=cv2.split(ycrcb)
    cv2.equalizeHist(channels[0],channels[0])
    cv2.merge(channels,ycrcb)
    cv2.cvtColor(ycrcb,cv2.COLOR_YCR_CB2BGR,img)
    return img

# loop over frames from the video file stream
while True:
    try:
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speedup processing)
        frame = vs.read()
        frame = imutils.resize(frame, width=512)
        
        yuvFrame = cv2.cvtColor(frame,cv2.COLOR_BGR2YUV)
        channels=cv2.split(yuvFrame)
        
        reConverted = cv2.cvtColor(channels[0],cv2.COLOR_GRAY2BGR)
        
        #cv2.imwrite("orig.jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        #cv2.imwrite("brightened.jpg", reConverted, [cv2.IMWRITE_JPEG_QUALITY, 100])
        #break

        # Detect the face boxes
        startTime = time.time()
        boxes = face_recognition.face_locations(frame, number_of_times_to_upsample=0, model="hog")
        elapsedTime = time.time() - startTime
        
        print( "Detection Time: " + str(elapsedTime) )
        
        for (top, right, bottom, left) in boxes:
            centerX = (left + right) / 2.0
            centerY = (top + bottom) / 2.0
            print("Face Detected: (" + str(centerX) + "," + str(centerY) + ")")
        
    except Exception as e:
        print(e)
        print("exiting")
        break
        
# do a bit of cleanup
#cv2.destroyAllWindows()
vs.stop()
