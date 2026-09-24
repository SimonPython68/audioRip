
import requests
import yt_dlp


def check_url(url):
    """Check whether the URL returns HTTP 200."""

    try:
        response = requests.get(
            url,
            stream=True,
            timeout=15
        )

        status_code = response.status_code
        response.close()

        if status_code == 200:
            print("URL check passed: HTTP 200")
            return True

        print(f"URL check failed: HTTP {status_code}")
        return False

    except requests.RequestException as error:
        print(f"Could not access URL: {error}")
        return False


def download_audio(url):
    """Download audio and convert it to MP3."""

    options = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        print("Download complete!")

    except Exception as error:
        print(f"Download failed: {error}")


def main():
    url = input("Enter the video URL: ").strip()

    if not url:
        print("No URL entered.")
        return

    if check_url(url):
        download_audio(url)
    else:
        print("Download cancelled: URL check failed.")


if __name__ == "__main__":
    main()
