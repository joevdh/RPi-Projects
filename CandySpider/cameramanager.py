from Shared import *
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import threading
import face_recognition
import time
import numpy as np
import cv2
from pupil_apriltags import Detector


# Camera information
FRAMERATE = 50

# Tag information
TAG_SIZE = .106
TAG_FAMILIES = "tagStandard41h12"

HEAD_WIDTH = 0.1

camera_info = {}

RESOLUTION = (640, 480)
# Camera Resolution
camera_info["res"] = RESOLUTION

# Camera Intrinsic Matrix (3x3)
camera_info["K"] = np.array([[576.934028905961, 0.0, 320.44740253522497],
                             [0.0, 576.7834994185702, 252.9979833948558],
                             [0.0, 0.0, 1.0]])

# The non-default elements of the K array, in the AprilTag specification
camera_info["params"] = [576.934, 576.783, 320.447, 252.998]

# Fisheye Camera Distortion Matrix
camera_info["D"] = np.array([[0.33811303762215894], [2.127039047309599], [-14.330835990951366], [28.997372956196564]])


# Fisheye flag
camera_info["fisheye"] = True
camera_info["map_1"], camera_info["map_2"] = cv2.fisheye.initUndistortRectifyMap(camera_info["K"], camera_info["D"],
                                                                                 np.eye(3), camera_info["K"],
                                                                                 camera_info["res"], cv2.CV_16SC2)


class CameraManager:
    def __init__(self):
        # Public members
        self.detected_tags = []
        self.detected_faces = []
        self.mutex : threading.Lock = threading.Lock()
        
        # initialize the camera
        self.camera = PiCamera()

		# set camera parameters
        self.camera.resolution = RESOLUTION
        self.camera.framerate = FRAMERATE

        # set optional camera parameters (refer to PiCamera docs)
        #self.camera.shutter_speed = int(1000000 / (3 * 50))    # Reduce the shutter speed to reduce blur, given in microseconds
        # for (arg, value) in kwargs.items():
        # 	setattr(self.camera, arg, value)

        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=RESOLUTION)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        # initialize the variable used to indicate if the thread should be stopped
        self.stopped = False
        
        #self.detector : Detector = Detector(families=TAG_FAMILIES, nthreads=1)
        self.imageTimeStamp : float = 0.0
        
        self.thread : Thread = Thread(target=self.ThreadFunc)
        self.thread.daemon = True
        self.thread.start()
    
    def __del__(self):
        self.Stop()
        
    def Stop(self):
        if self.stopped is False:
            print("Camera Manager Stopping")
            self.stopped = True
            self.thread.join()
            print("Camera Manager Stopped")
        
    def ThreadFunc(self):
        print("Camera Thread Running...")
        
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            #print( str(time.time()) + " New Image" )
            
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            frame = f.array
            self.rawCapture.truncate(0)
            
            # save the time when the image was taken
            self.imageTimeStamp = time.time()
            
            try:
                # Remove fisheye distortion
                image_undistorted = self.undistort(frame)
                
                #self.DetectTags(image_undistorted)
                self.DetectFaces(image_undistorted)
                
                #print( str(time.time()) + " Image Processing Done"  )
                
            except Exception as e:
                print("Camera Thread: " + str(e))
                self.stopped = True

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
            
    def DetectFaces(self, frame):
        # resize it to 500px (to speedup processing)
        #frame = imutils.resize(frame, width=512)
        
        # Detect the face boxes
        startTime = time.time()
        boxes = face_recognition.face_locations(frame, number_of_times_to_upsample=0, model="hog")
        elapsedTime = time.time() - startTime
        
        #print( "  Detection Time: " + str(elapsedTime) )
        
        if boxes is not None and len(boxes) > 0:
            with self.mutex:
                self.detected_faces = []
                
                for (top, right, bottom, left) in boxes:
                    print("  FaceDetected: " + str(time.time()))
                    # find the pixel at the center of the box around the face
                    centerX = (left + right) / 2.0
                    centerY = (top + bottom) / 2.0
                    
                    # convert it to a 3D coordinate relative to the camera
                    fx, fy, cx, cy = camera_info["params"]
                    
                    depth = 1.0
                    posX = (centerX - cx) * depth / fx
                    posY = (centerY - cy) * depth / fy
                    posZ = depth
                    
                    facePosLS : Vector3 = Vector3( posZ, -posX, -posY ).normalize()
                    
                    # Add it to the list of detected faces
                    self.detected_faces.append( Location(Transform(facePosLS), self.imageTimeStamp) )
    
    def DetectTags(self, img):
        # Convert the image to YUV format
        yuvImage = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        res = yuvImage.shape
        
        # Get the Y component which is the gray image
        image_raw = np.frombuffer(yuvImage, dtype=np.uint8,count=res[0] * res[1]).reshape(res[1], res[0])

        # Apply Histogram normalization to attempt to make the white and black parts of the image more distinct
        image_enhanced = cv2.equalizeHist(image_raw)

        # Detect tags on undistorted image
        tagsFound = self.detector.detect(image_enhanced, estimate_tag_pose=True, camera_params=camera_info["params"], tag_size = TAG_SIZE)
        
        with self.mutex:
            self.detected_tags = tagsFound
    
    def undistort(self, img):
        return cv2.remap( img, camera_info["map_1"], camera_info["map_2"], interpolation=cv2.INTER_LINEAR )



if __name__ == '__main__':
    camMgr=CameraManager()
    
    try:
        while True:
            time.sleep(0.1)
            for location in camMgr.detected_faces:
                if ( time.time() - location.timeStamp < 0.5 ):
                    angles = VectorToAngles( camMgr.detected_faces[0].transform.position )
                    print("Face Detected at " + str(angles) )
           
        print("shutting down camera manager") 
        
        
    except KeyboardInterrupt:
        print("Exiting...")
        
    finally:
        camMgr.Stop()
    