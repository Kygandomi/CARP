#!/usr/bin/env
import numpy as np
import cv2

cap = cv2.VideoCapture(1)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.resize(frame,(0,0), fx=0.2, fy=0.2) 

    cv2.imshow('orig', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
