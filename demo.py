import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json

# TODO: figure out good way to slow down

# Create gesture recognizer
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
allowed_gestures=np.array(["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "ILoveYou"])
options = vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            canned_gesture_classifier_options=mp.tasks.vision.ImageClassifierOptions(allowed_gestures)
        )

recognizer = vision.GestureRecognizer.create_from_options(options)

# Live video from webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Establish key points
x_min = 0
y_min = 0
x_max = 1280
y_max = 720
half_y = int(y_max / 2)
all_min = 460
all_max = 820


def get_track(hand_x, hand_y):
    # Using cartesian quadrants
    if hand_x >= all_min and hand_x <= all_max:
        return "All"

    # Left side
    if hand_x < all_min:
        # Top left
        if hand_y >= half_y:
            return "Percussion"
        # Bottom left
        else:
            return "Keys?"
    # Right side
    else:
        # Top right
        if hand_y >= half_y:
            return "Vocals"
        # Bottom right
        else:
            return "Strings"


def get_command(gesture):



def run():
# TODO: add delay so moving to section doesnt accidentally cause change
# TODO: ensure gesture has to change for effect to happen
#  (no unintentional rapid increase in volume)

    while True:
        success, frame = cap.read()

        if not success:
            break

        # Flip the frame horizontally (so it looks like a mirror)
        frame_display = cv2.flip(frame, 1)

        # Add section lines
        cv2.line(frame_display, (all_max, half_y), (x_max, half_y), (0, 0, 0), thickness=5)
        cv2.line(frame_display, (x_min, half_y), (all_min, half_y), (0, 0, 0), thickness=5)
        cv2.rectangle(frame_display, (all_min, y_min), (all_max, y_max), color=(0, 0, 0), thickness=5)

        # Convert the frame to RBG for mediapipe
        frame_input = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Get current timestamp
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        # Detect gestures
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_display)
        recognition_result = (recognizer.recognize_for_video(mp_image, timestamp_ms))

        gesture = "None"
        for result in recognition_result.gestures:
            gesture = result[0].category_name


        for result in recognition_result.hand_landmarks:
            norm_x = result[0].x
            norm_y = result[0].y
            hand_x = norm_x * x_max
            hand_y = norm_y * y_max

        track = get_track(hand_x, hand_y)
        command = get_command(gesture)


        fname = "results.json"
        with open(fname, 'w') as file:
            json.dump(results, file)

        cv2.imshow("Live Stream", frame_display)

        # End video capture by pressing 'q'
        if cv2.waitKey(1) == ord('q'):
            break

    # Ensure the window closes and free up resources
    cv2.destroyAllWindows()
    cap.release()



if __name__ == '__main__':
    run()