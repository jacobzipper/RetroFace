from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import io
import sys
from thread import start_new_thread
import RPi.GPIO as GPIO
stream = io.BytesIO()
camera = PiCamera()
camera.resolution = (120, 80)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(120, 80))
camera.capture(stream, format='jpeg')
left = 11
right = 12
up = 13
down = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(left,GPIO.OUT)
GPIO.setup(right,GPIO.OUT)
GPIO.setup(up,GPIO.OUT)
GPIO.setup(down,GPIO.OUT)
GPIO.output(left,GPIO.HIGH)
GPIO.output(right,GPIO.HIGH)
GPIO.output(up,GPIO.HIGH)
GPIO.output(down,GPIO.HIGH)
time.sleep(0.1)
direc=""
buff = np.fromstring(stream.getvalue(), dtype=np.uint8)
image = cv2.imdecode(buff, 1)
face_cascade = cv2.CascadeClassifier('/home/pi/cascades/haarcascade_frontalface_alt.xml')
inThread = False
face = []
zero = []
def faceDetect(image):
	global inThread
	global face_cascade
	global face
	global zero
	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.1, 5)
	if zero==[] and len(face) > 0:
		print "zeroed"
		zero = [face[0][0]+face[0][2]/2,face[0][1] + face[0][3]/2]
	inThread = False
def leftOrRight(center):
        global zero
	if center[0] > zero[0]+10:
		return "left"
	elif center[0] < zero[0]-10:
		return "right"
	else:
		return "center"
def upOrDown(center):
        global zero
        if center[1] > zero[1]+5:
                return "down"
        elif center[1] < zero[1]-5:
                return "up"
        else:
                return "center"
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
	if not inThread:
		inThread = True
		start_new_thread(faceDetect,(image,))
	for (x,y,w,h) in face:
		if zero!=[]:
			direc = leftOrRight([x+w/2,y+h/2])
			print direc
			if direc=="left":
				GPIO.output(left,GPIO.HIGH)
				GPIO.output(right,GPIO.LOW)
			elif direc=="right":
				GPIO.output(right,GPIO.HIGH)
				GPIO.output(left,GPIO.LOW)
			else:
				GPIO.output(right,GPIO.LOW)
                                GPIO.output(left,GPIO.LOW)
			direc = upOrDown([x+w/2,y+h/2])
			print direc
                        if direc=="up":
                                GPIO.output(up,GPIO.HIGH)
                                GPIO.output(down,GPIO.LOW)
                        elif direc=="down":
                                GPIO.output(down,GPIO.HIGH)
                                GPIO.output(up,GPIO.LOW)
			else:
                                GPIO.output(up,GPIO.LOW)
                                GPIO.output(down,GPIO.LOW)
        rawCapture.truncate(0)

