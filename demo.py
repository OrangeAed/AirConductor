import cv2
import numpy as np
import mediapipe as mp

cap = cv2.VideoCapture(0)
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

while True:
    success, frame = cap.read()

    if not success:
        break

    # Flip the frame horizontally (so it looks like a mirror)
    frame = cv2.flip(frame, 1)

    cv2.imshow("Live Stream", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
