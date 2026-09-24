import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
import yt_dlp


class AudioDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Audio Downloader")
        self.root.geometry("650x430")
        self.root.resizable(False, False)

        self.download_folder = os.path.expanduser("~/Downloads")

        self.create_gui()

    def create_gui(self):
        # Main frame
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        # Title
        title = ttk.Label(
            main,
            text="YT Audio Downloader",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 20))

        # URL label
        ttk.Label(
            main,
            text="Video URL:"
        ).pack(anchor="w")

        # URL entry
        self.url_entry = ttk.Entry(main, width=75)
        self.url_entry.pack(fill="x", pady=(5, 15))

        # Download location
        ttk.Label(
            main,
            text="Download location:"
        ).pack(anchor="w")

        location_frame = ttk.Frame(main)
        location_frame.pack(fill="x", pady=(5, 15))

        self.folder_entry = ttk.Entry(location_frame)
        self.folder_entry.insert(0, self.download_folder)
        self.folder_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.browse_button = ttk.Button(
            location_frame,
            text="Browse...",
            command=self.choose_folder
        )
        self.browse_button.pack(side="right", padx=(10, 0))

        # Download button
        self.download_button = ttk.Button(
            main,
            text="Download Audio",
            command=self.start_download
        )
        self.download_button.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            main,
            orient="horizontal",
            length=600,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        # Status
        self.status_label = ttk.Label(
            main,
            text="Ready"
        )
        self.status_label.pack(pady=5)

        # Output box
        ttk.Label(
            main,
            text="Status:"
        ).pack(anchor="w", pady=(10, 2))

        self.output = tk.Text(
            main,
            height=7,
            width=75,
            state="disabled"
        )
        self.output.pack(fill="both", expand=True)

    def choose_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.download_folder
        )

        if folder:
            self.download_folder = folder

            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def log(self, message):
        self.output.config(state="normal")
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def set_status(self, message):
        self.status_label.config(text=message)

    def check_url(self, url):
        try:
            self.log("Checking URL...")

            response = requests.get(
                url,
                stream=True,
                timeout=15,
                allow_redirects=True
            )

            status = response.status_code
            response.close()

            self.log(f"HTTP status: {status}")

            return status == 200

        except requests.RequestException as error:
            self.log(f"URL check failed: {error}")
            return False

    def progress_hook(self, data):
        if data["status"] == "downloading":

            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes")

            if total:
                percentage = downloaded / total * 100

                self.root.after(
                    0,
                    lambda: self.progress.config(
                        value=percentage
                    )
                )

                self.root.after(
                    0,
                    lambda: self.set_status(
                        f"Downloading... {percentage:.1f}%"
                    )
                )

        elif data["status"] == "finished":

            self.root.after(
                0,
                lambda: self.progress.config(value=100)
            )

            self.root.after(
                0,
                lambda: self.set_status(
                    "Converting audio..."
                )
            )

    def download(self, url, folder):

        try:
            # Check URL first
            if not self.check_url(url):

                self.root.after(
                    0,
                    lambda: self.set_status(
                        "URL check failed"
                    )
                )

                self.root.after(
                    0,
                    lambda: self.log(
                        "Download cancelled."
                    )
                )

                return

            self.root.after(
                0,
                lambda: self.set_status(
                    "URL OK - starting download..."
                )
            )

            self.root.after(
                0,
                lambda: self.log(
                    "Starting yt-dlp..."
                )
            )

            options = {
                "format": "bestaudio/best",

                "outtmpl": os.path.join(
                    folder,
                    "%(title)s.%(ext)s"
                ),

                "noplaylist": True,

                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],

                "progress_hooks": [
                    self.progress_hook
                ],

                "quiet": True,

                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            self.root.after(
                0,
                lambda: self.set_status(
                    "Download complete!"
                )
            )

            self.root.after(
                0,
                lambda: self.log(
                    f"Saved to: {folder}"
                )
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Complete",
                    "Audio download completed successfully!"
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.set_status(
                    "Download failed"
                )
            )

            self.root.after(
                0,
                lambda: self.log(
                    f"Error: {error}"
                )
            )

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Download Error",
                    str(error)
                )
            )

        finally:

            self.root.after(
                0,
                lambda: self.download_button.config(
                    state="normal"
                )
            )

            self.root.after(
                0,
                lambda: self.browse_button.config(
                    state="normal"
                )
            )

    def start_download(self):

        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "Missing URL",
                "Please enter a video URL."
            )
            return

        if not folder:
            messagebox.showwarning(
                "Missing folder",
                "Please select a download folder."
            )
            return

        if not os.path.isdir(folder):
            messagebox.showerror(
                "Invalid folder",
                "The selected download folder does not exist."
            )
            return

        # Reset progress
        self.progress.config(value=0)

        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")

        self.download_button.config(
            state="disabled"
        )

        self.browse_button.config(
            state="disabled"
        )

        # Run download in background
        thread = threading.Thread(
            target=self.download,
            args=(url, folder),
            daemon=True
        )

        thread.start()


# Start application
if __name__ == "__main__":

    root = tk.Tk()

    app = AudioDownloader(root)

    root.mainloop()