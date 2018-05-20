# USAGE
# python test_network.py --model santa_not_santa.model --image images/examples/santa_01.png

# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import pickle
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to trained model model")
# ap.add_argument("-l", "--labelbin", required=True,
# 	help="path to label binarizer")
#ap.add_argument("-i", "--image", required=True,
	#help="path to input image")
args = vars(ap.parse_args())

# Load model
MODEL_PATH = args["model"]
# load the trained convolutional neural network and labels
print("[INFO] loading network...")
model = load_model(MODEL_PATH)
# lb = pickle.loads(open(args["labelbin"], "rb").read())


# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()

#vs = cv2.VideoCapture(args["video"])
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	#ret, frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# prepare the image to be classified by our deep learning network
	image = cv2.resize(frame, (32, 32))
	image = image.astype("float") / 255.0
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)


	

	# classify the input image and initialize the label and
	# probability of the prediction
	# classify the input image
	(No_Target, Target) = model.predict(image)[0]

	# build the label
	prob_array = np.array([No_Target, Target])
	x = np.argmax(prob_array)
	if x == 1:
		label = "Target"
	else:
		label = "No Target"

	# build the label and draw it on the frame
	label = "{}: {:.2f}%".format(label, proba[idx] * 100)
	output = imutils.resize(frame, width=1200)
	cv2.putText(output, label, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,
	0.7, (0, 0,0), 2)

	# show the output frame
	cv2.imshow("Frame", output)
	key = cv2.waitKey(25) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
 
# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
time.sleep(2.0)
vs.stop()