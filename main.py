import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Configured according to images of size 1280 x 720
#variables
width, height = 1280, 720
folderpath = "Presentations"
imgNumber = 0
hs, ws = int(120*2), int(213*2)
gestureLimit = 400
buttonPressed = False
buttonCounter = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False

#Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


#Camera setup
cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)

#List of presentation images
pathImages = sorted(os.listdir(folderpath), key=len)
# print(pathImages)

while True:
    #Importing images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderpath,pathImages[imgNumber])
    imgcurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)
    cv2.line(img,(0,gestureLimit),(width,gestureLimit),(0,255,0),10)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx,cy = hand['center']
        lmList = hand['lmList']

        # constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0],[width//2,w],[0,width]))
        yVal = int(np.interp(lmList[8][1],[150,height-150],[0,height]))
        indexFinger = xVal, yVal
        # print(fingers)

        if cy <= gestureLimit: #If hand is above limit
            annotationStart = False
            #Gesture Left - Previous slide
            if fingers == [1,0,0,0,0]:
                annotationStart = False
                print("Left")
                if imgNumber >0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1

            #Gesture Right - Next slide
            if fingers == [0,0,0,0,1]:
                annotationStart = False
                print("Right")
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1

        #Gesture Show pointer
        if fingers == [0,1,1,0,0]:
            cv2.circle(imgcurrent,indexFinger,12,(0,0,255),cv2.FILLED)
            annotationStart = False

        #Gesture Draw
        if fingers == [0,1,0,0,0]: # can draw only with index finger
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgcurrent,indexFinger,12,(0,0,255),cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        #Gesture Erase
        if fingers == [0,1,1,1,0]:
            if annotations:
                if annotationNumber >= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

    else:
        annotationStart = False

    #Button Pressed Iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgcurrent,annotations[i][j-1], annotations[i][j],(0,0,200),12)

    #Adding webcam image on the slides
    imgsmall = cv2.resize(img,(ws,hs))
    h, w ,_ = imgcurrent.shape
    imgcurrent[0:hs,w-ws:w] = imgsmall

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgcurrent)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
