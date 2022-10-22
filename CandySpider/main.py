import numpy as np
import cv2
from time import sleep, time
from picamera import PiCamera
from candy_spider import CandySpider

MAX_TIME = 30

# Camera information
FPS = 50
RES = (640, 480)

camera_info = {}

# Camera Resolution
camera_info["res"] = RES

# Camera Intrinsic Matrix (3x3)
camera_info["K"] = np.array([[576.934028905961, 0.0, 320.44740253522497],
                             [0.0, 576.7834994185702, 252.9979833948558],
                             [0.0, 0.0, 1.0]])

# The non-default elements of the K array, in the AprilTag specification
camera_info["params"] = [576.934, 576.783, 320.447, 252.998]

# Fisheye Camera Distortion Matrix
camera_info["D"] = np.array([[0.33811303762215894],
                             [2.127039047309599],
                             [-14.330835990951366],
                             [28.997372956196564]])

# Fisheye flag
camera_info["fisheye"] = True
camera_info["map_1"], camera_info["map_2"] = cv2.fisheye.initUndistortRectifyMap(camera_info["K"], camera_info["D"],
                                                                                 np.eye(3), camera_info["K"],
                                                                                 camera_info["res"], cv2.CV_16SC2)

# Create the camera object
with PiCamera() as camera:
    camera.resolution = RES
    camera.framerate = FPS
    # Reduce the shutter speed to reduce blur, given in microseconds
    camera.shutter_speed = int(1000000 / (3 * FPS))

    # Create the stream object
    candySpider : CandySpider = CandySpider( camera_info )
    sleep(1)
    print("Starting")
    
    try:
        # Start recording frames to the stream object
        camera.start_recording(candySpider, format='yuv')
        t0 = time()

        print("Running")

        while True:
            camera.wait_recording(1)
            
            if (candySpider.activity is None):
                break
            
            # If the time limit is reached, end the recording
            if (time() - t0) > MAX_TIME:
                break

    except Exception as e:
        print(e)
        
    finally:
        print("Stopping")
        camera.stop_recording()
        candySpider.Shutdown()
