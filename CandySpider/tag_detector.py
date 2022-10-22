##########################################################
# Detects April Tags within an image and estimates their pose
##########################################################

import numpy as np
from pupil_apriltags import Detector
import cv2
from time import sleep
from time import time as Time


# Tag information
TAG_SIZE = .106
TAG_FAMILIES = "tagStandard41h12"

TAG_DETECTION_INTERVAL = 0.05

class TagDetector():

    def __init__(self, camera_info):
        
        # Create Apriltags Detector
        self.detector = Detector(families=TAG_FAMILIES, nthreads=1)
        
        # Settings
        self.tag_size = TAG_SIZE
        self.camera_info = camera_info
        self.res = camera_info["res"]

        self.nextUpdateTime = 0
        
        # Results
        self.detected_tags = []

    def IsReady(self):
        return Time() >= self.nextUpdateTime

    # Runs tag detection on the given image.  
    # Returns true if a tag is found, false if no tags are found or not enough time has passes since the last detection
    def RunDetection(self, data):
       
        if (Time() < self.nextUpdateTime):
            return False
        
        self.detected_tags = []
        
        # Get the Y component which is the gray image
        image_raw = np.frombuffer(data,dtype=np.uint8,count=self.res[0] * self.res[1]).reshape(self.res[1], self.res[0])

        # Remove fisheye distortion
        image_undistorted = self.undistort(image_raw)
        
        # Apply Histogram normalization to attempt to make the white and black parts of the image more distinct
        image_enhanced = cv2.equalizeHist(image_undistorted)

        # Detect tags on undistorted image
        self.detected_tags = self.detector.detect(image_enhanced, estimate_tag_pose=True, camera_params=self.camera_info["params"], tag_size=self.tag_size)
        
        self.nextUpdateTime = Time() + TAG_DETECTION_INTERVAL
        
        return ( len(self.detected_tags) > 0 )

    def undistort(self, img):
        return cv2.remap(img, self.camera_info["map_1"], self.camera_info["map_2"], interpolation=cv2.INTER_LINEAR)
    
