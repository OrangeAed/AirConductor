import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components.processors import ClassifierOptions
import json
from gesture_data_publisher import DataPublisher
from threading import Thread


class GestureRecognizer:
    def __init__(self, queue):
        self.queue = queue

        # Initialize gesture recognizer
        self.base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        self.allowed_gestures = np.array(["None", "Closed_Fist", "Pointing_Up", "Thumb_Down", "Thumb_Up", "ILoveYou"])
        self.options = vision.GestureRecognizerOptions(
            base_options=self.base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            canned_gesture_classifier_options=ClassifierOptions(category_allowlist=self.allowed_gestures.tolist()),
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Section boundaries
        self.x_min = 0
        self.y_min = 0
        self.x_max = 1280
        self.y_max = 720
        self.half_y = int(self.y_max / 2)
        self.all_min = 460
        self.all_max = 820

        # Results dictionary
        self.results = {"speed": 0, "volume": 0, "playing": False}
        self.last_gesture = "None"

    def get_track(self, hand_x, hand_y):
        if self.all_min <= hand_x <= self.all_max:
            return "All"
        if hand_x < self.all_min:
            return "Percussion" if hand_y >= self.half_y else "Keys"
        return "Vocals" if hand_y >= self.half_y else "Strings"

    def update_results(self, track, gesture):
        match gesture:
            case "Closed_Fist":
                self.results["track"] = track
                self.results["playing"] = False
            case "ILoveYou":
                self.results["track"] = track
                self.results["playing"] = True
            case "Pointing_Up":
                self.results["track"] = track
                self.results["speed"] = 1
            case "Thumb_Up":
                self.results["track"] = track
                self.results["volume"] = 1
            case "Thumb_Down":
                self.results["track"] = track
                self.results["volume"] = -1

    def recognize_gesture(self, frame_display, timestamp_ms):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_display)
        recognition_result = self.recognizer.recognize_for_video(mp_image, timestamp_ms)

        gesture = "None"
        for result in recognition_result.gestures:
            gesture = result[0].category_name

        hand_x, hand_y = 0, 0
        for result in recognition_result.hand_landmarks:
            norm_x = result[0].x
            norm_y = result[0].y
            hand_x = norm_x * self.x_max
            hand_y = norm_y * self.y_max

        track = self.get_track(hand_x, hand_y)

        if gesture != self.last_gesture:
            self.update_results(track, gesture)
            self.last_gesture = gesture
            self.queue.put(self.results)

        with open("results.json", 'w') as file:
            file.write(json.dumps(self.results))

    def run(self):

        while True:
            success, frame = self.cap.read()
            if not success:
                break

            frame_display = cv2.flip(frame, 1)
            cv2.line(frame_display, (self.all_max, self.half_y), (self.x_max, self.half_y), (0, 0, 0), thickness=5)
            cv2.line(frame_display, (self.x_min, self.half_y), (self.all_min, self.half_y), (0, 0, 0), thickness=5)
            cv2.rectangle(frame_display, (self.all_min, self.y_min), (self.all_max, self.y_max), color=(0, 0, 0), thickness=5)

            timestamp_ms = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
            self.recognize_gesture(frame_display, timestamp_ms)

            cv2.imshow("Live Stream", frame_display)
            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()
        self.cap.release()

def make_and_run(queue):
    recognizer = GestureRecognizer(queue)
    recognizer.run()