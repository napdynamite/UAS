# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import imutils
from collections import deque
import argparse

#construct argumetns and parse
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help ="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

#initialize Picamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

#define lower and upper boundaries of RED color space in HSV
redLower = (169,100,100)
redUpper = (189, 255, 255)
pts = deque(maxlen=args["buffer"])

#if video path is not supplied, grab referecne to webcam
if not args.get("video", False):
    #capture from PiCamera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image - this array
	# will be 3D, representing the width, height, and # of channels
	image = frame.array
	
	#resize the frame, blur it and convert ot HSV
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	#construct a mask for color green, then perfrom
	#a series of dilations and erosions to remove small blobs in mask
	mask = cv2.inRange(hsv, redLower, redUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	#find contours in mask
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	#only proceed iuf atleat one contour is found
	if len(cnts)>0:
            #find largest contour in mask and compute enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x,y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)

            center = (int(M["m10"]/M["m00"]), int (M["m01"]/M["m00"]))

            #only proceed if the radius meets a minimum size
            if radius >10:
                #draw the circle and centroid in frame, update list of tracked points
                cv2.circle(image, (int(x), int(y)), int (radius), (0,255,255), 2)
                cv2.circle(image, center, 5, (0,0,255), -1)

        #update points queue
        pts.appendleft(center)

        #loop over set of tracked points
        for i in xrange(1, len(pts)):
            if pts[i -1] is None or pts[i] is None:
                continue

            #otherwise compute thickness of line
            thickness = int(np.sqrt(args["buffer"]/float(i+1))*2.5)
            cv2.line(image, pts[i -1], pts[i], (0,0,255), thickness)

        #show frame to screen
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	
    
    
