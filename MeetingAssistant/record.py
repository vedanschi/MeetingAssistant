# my_package/record.py

import subprocess

def record_screen():
    command = [
        "ffmpeg",
        "-f", "gdigrab",            # For screen capture on Windows
        "-framerate", "30",
        "-i", "desktop",
        "-f", "dshow",
        "-i", "audio=Microphone (Realtek)",  
        "meeting_recording.mp4"
    ]
    subprocess.run(command)

if __name__ == "__main__":
    record_screen()
