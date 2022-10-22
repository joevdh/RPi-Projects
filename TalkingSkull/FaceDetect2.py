from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import threading

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
#vs = VideoStream(src=0,framerate=1).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

DetectionDone = True
FaceBoxes = []
threads = list()

def run_detection(frame):
    global FaceBoxes
    global DetectionDone
    print("Running\n")
    FaceBoxes = face_recognition.face_locations(frame)
    print("Done\n")
    DetectionDone = True

# loop over frames from the video file stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    
    print(frame)
    
    if DetectionDone == True:
        for thread in threads:
            thread.join()
            
        for (top, right, bottom, left) in FaceBoxes:
            # draw the predicted face name on the image - color is in BGR
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        
        threads = []
        DetectionDone = False
        x = threading.Thread(target=run_detection, args=(frame,))
        threads.append(x)
        x.start()
    
    # Detect the fce boxes
    #boxes = face_recognition.face_locations(frame)
    
    #for (top, right, bottom, left) in boxes:
        # draw the predicted face name on the image - color is in BGR
     #   cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        
        
    # display the image to our screen
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    # quit when 'q' key is pressed
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
