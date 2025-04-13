from datetime import datetime, timedelta

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.processors import ClassifierOptions
import json

# TODO: control what is sent to wyatt (should only be when there is a change)

# Set up hand landmarks
mp_hands = mp.solutions.hands

# Create gesture recognizer
base_gesture_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
allowed_gestures = np.array(["None", "Closed_Fist", "Pointing_Up", "Thumb_Down", "Thumb_Up", "ILoveYou"])
gesture_options = vision.GestureRecognizerOptions(
    base_options=base_gesture_options,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    canned_gesture_classifier_options=ClassifierOptions(category_allowlist=["None",
                                                                            "Closed_Fist",
                                                                            "Pointing_Up",
                                                                            "Thumb_Down",
                                                                            "Thumb_Up",
                                                                            "ILoveYou"]),
)

recognizer = vision.GestureRecognizer.create_from_options(gesture_options)


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

# Initialize results dictionary
results = {"speed": 0, "volume": 0, "playing": False}


def get_track(hand_x, hand_y):
    # Using cartesian quadrants
    if hand_x >= all_min and hand_x <= all_max:
        return "c"

    # Left side
    if hand_x < all_min:
        # Upper left
        if hand_y <= half_y:
            return "ul"
        # Lower left
        else:
            return "ll"
    # Right side
    else:
        # Upper right
        if hand_y <= half_y:
            return "ur"
        # Lower right
        else:
            return "lr"


def update_results(track, gesture):
    match gesture:
        case "None":
            results["track"] = track
            results["speed"] = 0
            results["volume"] = 0
        case "Closed_Fist":
            results["track"] = track
            results["playing"] = False
        case "ILoveYou":
            results["track"] = track
            results["playing"] = True
        case "Pointing_Up":
            results["track"] = track
            results["speed"] = 1
        case "Pointing_Down":
            results["track"] = track
            results["speed"] = -1
        case "Thumb_Up":
            results["track"] = track
            results["volume"] = 1
        case "Thumb_Down":
            results["track"] = track
            results["volume"] = -1

def is_pointing_down(index, pinky, ring, middle, thumb):
    if index > thumb:
        if thumb > pinky and thumb > ring and thumb > middle:
            return True
    return False

def run(queue, timeout=100):
# TODO: add delay so moving to section doesnt accidentally cause change
# TODO: ensure gesture has to change for effect to happen
#  (no unintentional rapid increase in volume)
    last_gesture = "None"
    time = datetime.now()
    while datetime.now() < time + timedelta(seconds=timeout):
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
        frame_input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get current timestamp
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        # Recognize gestures
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_display)
        recognition_result = (recognizer.recognize_for_video(mp_image, timestamp_ms))

        gesture = "None"
        for result in recognition_result.gestures:
            gesture = result[0].category_name

        # Detect gesture location
        hand_x = 0
        hand_y = 0
        for result in recognition_result.hand_landmarks:
            norm_x = result[0].x
            norm_y = result[0].y
            hand_x = norm_x * x_max
            hand_y = norm_y * y_max

        track = get_track(hand_x, hand_y)

        # Detect landmarks
        hand = mp_hands.Hands()

        landmark_results = hand.process(frame_input)
        index = pinky = ring = middle = thumb = 0
        if landmark_results.multi_hand_landmarks:
            for hand_landmarks in landmark_results.multi_hand_landmarks:
                index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * y_max
                pinky = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y * y_max
                ring = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * y_max
                middle = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * y_max
                thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * y_max

        if is_pointing_down(index=index, pinky=pinky, ring=ring, middle=middle, thumb=thumb):
            gesture = "Pointing_Down"
            print("pointing down")

        # Update results if necessary
        if gesture != last_gesture:
            update_results(track, gesture)
            last_gesture = gesture
            queue.put(results)
            print(results)

        filename = "results.json"
        with open(filename, 'w') as file:
            file.write(json.dumps(results))

        cv2.imshow("Live Stream", frame_display)

        # End video capture by pressing 'q'
        if cv2.waitKey(1) == ord('q'):
            break

    # Ensure the window closes and free up resources
    cv2.destroyAllWindows()
    cap.release()



if __name__ == '__main__':
    import queue
    q = queue.Queue(1000)
    run(queue=q)
    while not q.empty():
        print(q.get())