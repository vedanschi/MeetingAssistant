# my_package/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess

def start_recording():
    subprocess.Popen(["python", "MeetingAssistant/record.py"])  # ✅ adjust path

def schedule_meeting_recording(meeting_time: str):
    dt = datetime.fromisoformat(meeting_time.replace("Z", "+00:00"))  # Ensure it's a valid ISO timestamp
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_recording, 'date', run_date=dt)
    scheduler.start()
