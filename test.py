import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands()

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='/path/to/model.task'),
    running_mode=VisionRunningMode.LIVE_STREAM)
# Set up camera feed
cap = cv2.VideoCapture(0)
while True:
    # ret : boolean, True if frame is successfully captured
    ret, frame = cap.read()

    # Flip frame to be mirror image
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB for compatability with mediapipe
    RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hand.process(RGB_frame)

    try:
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    except:
        cap.release()
        cv2.destroyAllWindows()

    # Display the feed
    cv2.imshow('Camera', frame)

    # Exit by pressing 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Free up the camera and close video window when done
cap.release()
cv2.destroyAllWindows()

