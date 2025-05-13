import subprocess
import requests
from datetime import datetime
import os

TELEGRAM_TOKEN = 'your-bot-token-here'
CHAT_ID = 'your-chat-id-here'

def send_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(file_path, 'rb') as video:
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": f"📹 Meeting recording: {os.path.basename(file_path)}"
        }, files={"video": video})
    if response.status_code == 200:
        print("✅ Uploaded to Telegram.")
    else:
        print(f"❌ Failed to upload: {response.text}")

def record_screen():
    filename = f"meeting_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-f", "gdigrab",
        "-framerate", "30",
        "-i", "desktop",
        "-f", "dshow",
        "-i", "audio=Microphone (Realtek)",  # Match your device name
        filename
    ]

    subprocess.run(command)

    # ⬆️ After recording ends, upload it
    send_to_telegram(filename)

if __name__ == "__main__":
    record_screen()

