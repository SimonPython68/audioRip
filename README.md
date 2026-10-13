# YouTube Audio Downloader

This is a mini project using **yt-dlp** to download audio from YouTube videos.

The `requirements.txt` file lists the necessary dependencies for the project.

## Setup

To set up the project, create a virtual environment and install the dependencies using `pip`.

### Latest Working Version

**`audiogui2.py`**  
**Last confirmed working:** 12.13, 13/10/2026
<img width="2465" height="2303" alt="PXL_20261013_105536155~2" src="https://github.com/user-attachments/assets/c4b5d5b2-64ce-43a5-9673-1286e0830314" />



## Imports

```python
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
import yt_dlp
