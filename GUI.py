import tkinter as tk
from tkinter import filedialog, ttk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("AIR CONDUCTOR")

    upload_button = tk.Button(root, text="Upload and Play MP3 File", command=lambda: None)
    upload_button.pack(pady=20)

    toggle_button = tk.Button(root, text="Play", command=lambda: None)
    toggle_button.pack(pady=20)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(pady=20, fill=tk.X)

    root.mainloop()