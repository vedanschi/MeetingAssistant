# my_package/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import subprocess

def start_recording():
    subprocess.Popen(["python", "my_package/record.py"])  # adjust path if needed

def schedule_meeting_recording(meeting_time: str):
    dt = datetime.fromisoformat(meeting_time)
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_recording, 'date', run_date=dt)
    scheduler.start()
