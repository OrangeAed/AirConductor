import os
import subprocess
import sys

import customtkinter as ctk
from tkinter import filedialog
from pydub import AudioSegment
from PIL import Image, ImageTk
import cv2

class AudioUploader:
    def __init__(self, root, queue):
        self.queue = queue
        # Application
        self.root = root
        self.root.title("Video Stream Upload")
        self.root.geometry("1500x1000")

        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # Can be "light", "dark", or "system"
        ctk.set_default_color_theme("blue")  # Other options: "green", "dark-blue"

        # Create main container frame
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Video stream display area
        self.video_label = ctk.CTkLabel(self.main_frame, text="Video Stream",
                                        font=("Arial", 20, "bold"),
                                        width=500, height=250)
        self.video_label.pack(pady=(10, 5))


        # Upload button
        self.upload_button = ctk.CTkButton(self.main_frame,
                                           text="Upload Audio File",
                                           command=self.upload_audio,
                                           width=200,
                                           height=40,
                                           corner_radius=8)
        self.upload_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.main_frame, text="",
                                         font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.cap = cv2.VideoCapture(0)
        self.update_video()

        self.output_filepath = ""

    def upload_audio(self):
        """Allow the user to upload a folder with multiple audio tracks."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            output_dir = "songs\\" + os.path.basename(folder_path)
            os.makedirs(output_dir, exist_ok=True)
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if file_name.endswith(".mp3"):
                    audio = AudioSegment.from_mp3(file_path)
                elif file_name.endswith(".wav"):
                    audio = AudioSegment.from_wav(file_path)
                else:
                    continue
                output_name = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.wav")
                audio.export(output_name, format="wav")

        self.output_filepath = output_dir
        self.root.quit()


    def update_video(self):
        """Simulate video stream functionality"""
        success, frame = self.cap.read()
        if success:
            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)

            # Convert the frame to RGB (from BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a PIL Image
            img = Image.fromarray(frame)

            # Convert the PIL Image to an ImageTk object
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the video_label with the new frame
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk

        # Schedule the next frame update
        self.root.after(10, self.update_video)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()


def create_and_run_gui(queue):
    root = ctk.CTk()
    app = AudioUploader(root, queue)
    root.mainloop()
    queue.put(app.output_filepath)