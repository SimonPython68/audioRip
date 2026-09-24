import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
import yt_dlp


class AudioDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YT Audio Downloader")
        self.root.geometry("750x600")
        self.root.minsize(700, 550)

        self.download_folder = os.path.expanduser(
            "~/Downloads/audio"
        )

        os.makedirs(
            self.download_folder,
            exist_ok=True
        )

        self.current_process = None

        self.create_gui()
        self.refresh_library()

    # --------------------------------------------------
    # GUI
    # --------------------------------------------------

    def create_gui(self):

        style = ttk.Style(self.root)
        style.configure(
            "App.TFrame",
            background="#eee6ff"
        )
        style.configure(
            "App.TLabel",
            background="#eee6ff",
            foreground="#302244"
        )
        style.configure(
            "App.TEntry",
            fieldbackground="#f7f2ff",
            foreground="#302244"
        )
        style.configure(
            "App.Horizontal.TProgressbar",
            troughcolor="#ddd0f5",
            background="#624397"
        )

        main = ttk.Frame(
            self.root,
            padding=20,
            style="App.TFrame"
        )
        main.pack(
            fill="both",
            expand=True
        )

        title = ttk.Label(
            main,
            text="Simon's yt-dlp Audio rips",
            font=("Arial", 22, "bold"),
            style="App.TLabel"
            
        )
        title.pack(pady=(0, 20))
        # URL
        ttk.Label(
            main,
            text="Video URL:",
            style="App.TLabel"
        ).pack(anchor="w")

        self.url_entry = ttk.Entry(main, style="App.TEntry")
        self.url_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        # Folder
        ttk.Label(
            main,
            text="Download location:",
            style="App.TLabel"
        ).pack(anchor="w")

        folder_frame = ttk.Frame(main)
        folder_frame.pack(
            fill="x",
            pady=(5, 15)
        )

        self.folder_entry = ttk.Entry(
            folder_frame,
            style="App.TEntry"
        )

        self.folder_entry.insert(
            0,
            self.download_folder
        )

        self.folder_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.browse_button = ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.choose_folder
        )

        self.browse_button.pack(
            side="right",
            padx=(10, 0)
        )

        # Download
        self.download_button = ttk.Button(
            main,
            text="Download Audio",
            command=self.start_download
        )

        self.download_button.pack(
            pady=10
        )

        # Progress
        self.progress = ttk.Progressbar(
            main,
            orient="horizontal",
            mode="determinate",
            style="App.Horizontal.TProgressbar"
        )

        self.progress.pack(
            fill="x",
            pady=10
        )

        self.status_label = ttk.Label(
            main,
            text="Ready",
            style="App.TLabel"
        )

        self.status_label.pack(
            pady=(0, 10)
        )

        # Library
        ttk.Label(
            main,
            text="Audio Library",
            font=("Arial", 14, "bold"),
            style="App.TLabel"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        list_frame = ttk.Frame(main)
        list_frame.pack(
            fill="both",
            expand=True
        )

        self.library_list = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            background="#f7f2ff",
            foreground="#302244",
            selectbackground="#9471d1",
            selectforeground="#ffffff",
            highlightbackground="#c9b7e8",
            highlightcolor="#9471d1"
        )

        self.library_list.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.library_list.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.library_list.config(
            yscrollcommand=scrollbar.set
        )

        self.library_list.bind(
            "<Double-Button-1>",
            lambda event: self.play_selected()
        )

        # Buttons
        controls = ttk.Frame(main)
        controls.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            controls,
            text="▶ Play",
            command=self.play_selected
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Button(
            controls,
            text="■ Stop",
            command=self.stop_playback
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            controls,
            text="↻ Refresh",
            command=self.refresh_library
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            controls,
            text="📁 Open Folder",
            command=self.open_audio_folder
        ).pack(
            side="right"
        )

        # Status
        ttk.Label(
            main,
            text="Status:",
            style="App.TLabel"
        ).pack(anchor="w")

        self.output = tk.Text(
            main,
            height=5,
            state="disabled",
            background="#f7f2ff",
            foreground="#302244",
            insertbackground="#302244",
            highlightbackground="#c9b7e8",
            highlightcolor="#9471d1"
        )

        self.output.pack(
            fill="x",
            pady=(5, 0)
        )

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    def log(self, message):

        self.output.config(
            state="normal"
        )

        self.output.insert(
            tk.END,
            message + "\n"
        )

        self.output.see(
            tk.END
        )

        self.output.config(
            state="disabled"
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def set_status(self, message):

        self.status_label.config(
            text=message
        )

    # --------------------------------------------------
    # Browse
    # --------------------------------------------------

    def choose_folder(self):

        folder = filedialog.askdirectory(
            initialdir=self.download_folder
        )

        if folder:

            self.download_folder = folder

            self.folder_entry.delete(
                0,
                tk.END
            )

            self.folder_entry.insert(
                0,
                folder
            )

            self.refresh_library()

    # --------------------------------------------------
    # Open folder
    # --------------------------------------------------

    def open_audio_folder(self):

        folder = self.folder_entry.get().strip()

        if not os.path.isdir(folder):

            os.makedirs(
                folder,
                exist_ok=True
            )

        subprocess.Popen(
            ["xdg-open", folder]
        )

    # --------------------------------------------------
    # Refresh library
    # --------------------------------------------------

    def refresh_library(self):

        folder = self.folder_entry.get().strip()

        if not folder:
            return

        os.makedirs(
            folder,
            exist_ok=True
        )

        self.library_list.delete(
            0,
            tk.END
        )

        files = []

        for filename in os.listdir(folder):

            if filename.lower().endswith(
                (
                    ".mp3",
                    ".m4a",
                    ".opus",
                    ".wav",
                    ".flac",
                    ".aac",
                    ".ogg"
                )
            ):
                files.append(filename)

        files.sort(
            key=lambda filename: os.path.getmtime(
                os.path.join(folder, filename)
            ),
            reverse=True
        )

        for filename in files:

            self.library_list.insert(
                tk.END,
                filename
            )

        self.log(
            f"Library: {len(files)} audio file(s)"
        )

    # --------------------------------------------------
    # Selected file
    # --------------------------------------------------

    def get_selected_file(self):

        selection = self.library_list.curselection()

        if not selection:

            messagebox.showinfo(
                "No selection",
                "Select an audio file first."
            )

            return None

        filename = self.library_list.get(
            selection[0]
        )

        folder = self.folder_entry.get().strip()

        return os.path.join(
            folder,
            filename
        )

    # --------------------------------------------------
    # Play
    # --------------------------------------------------

    def play_selected(self):

        filepath = self.get_selected_file()

        if not filepath:
            return

        if not os.path.isfile(filepath):

            messagebox.showerror(
                "File error",
                "The selected file no longer exists."
            )

            self.refresh_library()
            return

        self.stop_playback()

        try:

            self.current_process = subprocess.Popen(
                ["xdg-open", filepath]
            )

            self.log(
                f"Playing: {os.path.basename(filepath)}"
            )

            self.set_status(
                f"Playing: {os.path.basename(filepath)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Playback error",
                str(error)
            )

    # --------------------------------------------------
    # Stop
    # --------------------------------------------------

    def stop_playback(self):

        if self.current_process:

            try:
                self.current_process.terminate()
            except Exception:
                pass

            self.current_process = None

            self.set_status(
                "Playback stopped"
            )

    # --------------------------------------------------
    # Check URL
    # --------------------------------------------------

    def check_url(self, url):

        try:

            self.log(
                "Checking URL..."
            )

            response = requests.get(
                url,
                stream=True,
                timeout=15,
                allow_redirects=True
            )

            status = response.status_code

            response.close()

            self.log(
                f"HTTP status: {status}"
            )

            return status == 200

        except requests.RequestException as error:

            self.log(
                f"URL check failed: {error}"
            )

            return False

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def progress_hook(self, data):

        if data["status"] == "downloading":

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            total = data.get(
                "total_bytes"
            )

            if total:

                percentage = (
                    downloaded / total * 100
                )

                self.root.after(
                    0,
                    lambda: self.progress.config(
                        value=percentage
                    )
                )

                self.root.after(
                    0,
                    lambda: self.set_status(
                        f"Downloading... "
                        f"{percentage:.1f}%"
                    )
                )

        elif data["status"] == "finished":

            self.root.after(
                0,
                lambda: self.progress.config(
                    value=100
                )
            )

            self.root.after(
                0,
                lambda: self.set_status(
                    "Converting to MP3..."
                )
            )

    # --------------------------------------------------
    # Download
    # --------------------------------------------------

    def download(self, url, folder):

        try:

            # Check URL
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
                    "URL OK - downloading..."
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
                    "Download completed."
                )
            )

            self.root.after(
                0,
                self.refresh_library
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Complete",
                    "Audio download completed!"
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

    # --------------------------------------------------
    # Start download
    # --------------------------------------------------

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

        os.makedirs(
            folder,
            exist_ok=True
        )

        self.download_folder = folder

        self.progress.config(
            value=0
        )

        self.output.config(
            state="normal"
        )

        self.output.delete(
            "1.0",
            tk.END
        )

        self.output.config(
            state="disabled"
        )

        self.download_button.config(
            state="disabled"
        )

        self.browse_button.config(
            state="disabled"
        )

        thread = threading.Thread(
            target=self.download,
            args=(url, folder),
            daemon=True
        )

        thread.start()


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AudioDownloader(root)

    root.mainloop()