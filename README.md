# YouTube Audio Downloader

This is a mini project using **yt-dlp** to download audio from YouTube videos.

The `requirements.txt` file lists the necessary dependencies for the project.

## Setup

To set up the project, create a virtual environment and install the dependencies using `pip`.

### Latest Working Version

**`audiogui2.py`**  
**Last confirmed working:** 13:00, 24/09/2026

## Imports

```python
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
import yt_dlp
