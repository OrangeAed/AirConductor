import customtkinter as ctk
from tkinter import filedialog
from pydub import AudioSegment
from PIL import Image, ImageTk


class VideoStreamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Stream Upload")
        self.root.geometry("1800x1200")

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

    def upload_audio(self):
        """Simulate video upload functionality"""
        global audio, paused_pos, audio_length
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file_path:
            audio = AudioSegment.from_mp3(file_path)
            filename = file_path.split("/")[-1]
            filename = f"songs/{filename.split(".")[0]}.wav"
            audio.export(filename, format="wav")
            send_message(filename)


def send_message(message):
    """Sends a message to the audio processing functionality"""
    print(message)
    pass


if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoStreamApp(root)
    root.mainloop()