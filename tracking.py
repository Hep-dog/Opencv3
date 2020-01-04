#!/usr/bin/python3

import cv2
import zmq
import base64
import picamera
import numpy as np
from picamera.array import PiRGBArray

IP = '192.168.43.84'
#IP = '192.168.137.1'

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(640, 480))

context = zmq.Context()
footage_socket = context.socket(zmq.PAIR)
footage_socket.connect('tcp://%s:5555'%IP)

print(IP)

linePos_1 = 380
linePos_2 = 430
lineColorSet = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame_image = frame.array

    frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    retval, frame_findline = cv2.threshold(frame_findline, 0, 255, cv2.THRESH_OTSU)
    frame_findline = cv2.erode(frame_findline, None, iterations=6)

    colorPos_1 = frame_findline[linePos_1]
    colorPos_2 = frame_findline[linePos_2]

    try:
        lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
        lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

        lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
        lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)

        if lineColorCount_Pos1 == 0:
            lineColorCount_Pos1 = 1
        if lineColorCount_Pos2 == 0:
            lineColorCount_Pos1 = 1

        left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1-1]
        right_Pos1= lineIndex_Pos1[0][0]
        center_Pos1 = int( (left_Pos1+right_Pos1)/2 )

        left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2-1]
        right_Pos2= lineIndex_Pos2[0][0]
        center_Pos2 = int( (left_Pos2+right_Pos2)/2 )

        center = int( (center_Pos1+center_Pos2)/2 )

    except:
        center = None
        pass

    print(center)

    try:
        cv2.line(frame_image, (left_Pos1, (linePos_1+30)), (left_Pos1, (linePos_1-30)), (255, 128, 64), 5)
        cv2.line(frame_image, (right_Pos1, (linePos_1+30)), (right_Pos1, (linePos_1-30)), (64, 128, 255), 5)
        cv2.line(frame_image, (0, linePos_1), (640, linePos_1), (255, 255, 64), 1)

        cv2.line(frame_image, (left_Pos2, (linePos_1+30)), (left_Pos2, (linePos_1-30)), (255, 128, 64), 5)
        cv2.line(frame_image, (right_Pos2, (linePos_1+30)), (right_Pos2, (linePos_1-30)), (64, 128, 255), 5)
        cv2.line(frame_image, (0, linePos_2), (640, linePos_2), (255, 255, 64), 1)

        cv2.line(frame_image, ((center-20), int((linePos_1+linePos_2)/2), ((center+20), int(linePos_1+linePos_2)/2)), (0, 0, 0), 1)
        cv2.line(frame_image, ((center), int((linePos_1+linePos_2)/2+20), ((center), int(linePos_1+linePos_2)/2-20)), (0, 0, 0), 1)

    except:
        pass

    encoded, buffer = cv2.imencode('.jpg', frame_image)
    jpg_as_text = base64.b64encode(buffer)
    footage_socket.send(jpg_as_text)
    rawCapture.truncate(0)

