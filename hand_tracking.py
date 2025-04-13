from datetime import datetime, timedelta

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.processors import ClassifierOptions
import json

# Create gesture recognizer
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    canned_gesture_classifier_options=ClassifierOptions(category_allowlist=["None",
                                                                            "Closed_Fist",
                                                                            "Open_Palm",
                                                                            "Pointing_Up",
                                                                            "Thumb_Down",
                                                                            "Thumb_Up",
                                                                            "ILoveYou"]),
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

# Initialize results dictionary
results = {"speed": 0, "volume": 0, "playing": False}


def get_track(hand_x, hand_y):
    # Using cartesian quadrants
    if hand_x >= all_min and hand_x <= all_max:
        return "c"

    # Left side
    if hand_x < all_min:
        # Top left
        if hand_y <= half_y:
            return "ul"
        # Bottom left
        else:
            return "ll"
    # Right side
    else:
        # Top right
        if hand_y <= half_y:
            return "ur"
        # Bottom right
        else:
            return "lr"


def update_results(track, gesture):
    match gesture:
        case "None":
            results["track"] = track
            results["speed"] = 0
            results["volume"] = 0
            print("None")
        case "Closed_Fist":
            results["track"] = track
            results["playing"] = False
            print("PAUSE")
        case "ILoveYou":
            results["track"] = track
            results["playing"] = True
            print("PLAY")
        case "Pointing_Up":
            results["track"] = track
            results["speed"] = 1
            print("SPEED UP")
        case "Open_Palm":
            results["track"] = track
            results["speed"] = -1
            print("SLOW DOWNq")
        case "Thumb_Up":
            results["track"] = track
            results["volume"] = 1
            print("VOLUME UP")
        case "Thumb_Down":
            results["track"] = track
            results["volume"] = -1
            print("VOLUME DOWN")


def run(queue, timeout=100):
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

        # Add labels
        # cv2.putText(frame_display, all_label, all_label_pos, font)

        # Get current timestamp
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        # Detect gestures
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_display)
        recognition_result = (recognizer.recognize_for_video(mp_image, timestamp_ms))

        gesture = "None"
        for result in recognition_result.gestures:
            gesture = result[0].category_name
            score = result[0].score
            print(f"{gesture} with {score} confidence")

        # Detect gesture location
        hand_x = 0
        hand_y = 0
        for result in recognition_result.hand_landmarks:
            norm_x = result[0].x
            norm_y = result[0].y
            hand_x = norm_x * x_max
            hand_y = norm_y * y_max

        track = get_track(hand_x, hand_y)

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
