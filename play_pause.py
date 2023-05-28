import cv2
import time
import pyautogui
import mediapipe as mp

wCam, hCam = 1000, 500

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

tipIds = [4, 8, 12, 16, 20]

prevFingerState = -1
playPauseDelay = 1.0  # Delay in seconds
prevActionTime = time.time()

isFullscreen = False

actions = {
    0: "Pause",
    5: "Play",
    1: "Full Screen",
    2: "Exit Full Screen",
    3: "Volume Up",
    4: "Volume Down"
}

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            fingers = []
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            totalFingers = fingers.count(1)

            if totalFingers in actions:
                actionText = actions[totalFingers]
                cv2.putText(img, actionText, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,cv2.FILLED)

            if totalFingers == 0:
                if prevFingerState != 0:
                    # Pause the music only if the previous state was not a closed hand
                    currentTime = time.time()
                    if currentTime - prevActionTime >= playPauseDelay:
                        pyautogui.press('space')
                        prevActionTime = currentTime
                prevFingerState = 0
            elif totalFingers == 5:
                if prevFingerState != 5:
                    # Play the music only if the previous state was not an open hand
                    currentTime = time.time()
                    if currentTime - prevActionTime >= playPauseDelay:
                        pyautogui.press('space')
                        prevActionTime = currentTime
                prevFingerState = 5

            if totalFingers == 1:
                if not isFullscreen:
                    pyautogui.press('f')  # Press 'f' to enter full screen
                    isFullscreen = True
            elif totalFingers == 2:
                if isFullscreen:
                    pyautogui.press('esc')  # Press 'esc' to exit full screen
                    isFullscreen = False
            elif totalFingers == 3:
                pyautogui.press('volumeup')  # Press 'volumeup' to increase volume
            elif totalFingers == 4:
                pyautogui.press('volumedown')  # Press 'volumedown' to decrease volume

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3,cv2.FILLED)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
