import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
# mp_hands = mp.solutions.hands


# options = vision.GestureRecognizerOptions(base_options=base_options,
#                                           running_mode = vision.RunningMode.LIVE_STREAM,
#                                           result_callback=save_result)



# Live video from webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    success, frame = cap.read()

    if not success:
        break

    # Flip the frame horizontally (so it looks like a mirror)
    frame_display = cv2.flip(frame, 1)

    # Convert the frame to RBG for mediapipe
    frame_input = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)




    cv2.imshow("Live Stream", frame_display)

    # End video capture by pressing 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Ensure the window closes and free up resources
cv2.destroyAllWindows()
cap.release()
