# gui_launcher.py - PySimpleGUI launcher for MeetingAssistant

import os
import sys
import shutil
import subprocess
from datetime import datetime
import PySimpleGUI as sg

# Import the project modules
import modules.transcribe as transcription
import modules.summarize as summarization
import modules.search as search_module

# Ensure required directories exist
os.makedirs('meetings', exist_ok=True)
os.makedirs('models', exist_ok=True)  # if models used by transcription/summarization

# GUI layout
sg.theme('LightBlue2')

layout = [
    [sg.Text('Telegram Bot:'), sg.Button('Launch Telegram Bot', key='-BOT-')],
    [sg.HorizontalSeparator()],
    
    [sg.Text('Meeting Title:'), sg.Input(key='-TITLE-', size=(30,1))],
    [sg.Text('Select audio/video file:'), sg.Input(key='-FILE-', size=(50,1)), sg.FileBrowse(
        file_types=(("Audio/Video Files","*.mp3;*.wav;*.mp4;*.mkv;*.mov"),)
    )],
    [sg.Button('Transcribe & Summarize', key='-PROCESS-')],
    [sg.Multiline('', size=(80,10), key='-LOG-', autoscroll=True, disabled=True)],
    [sg.HorizontalSeparator()],
    
    [sg.Text('Search previous summaries:'), sg.Input(key='-SEARCH-', size=(50,1)), sg.Button('Search', key='-DOSEARCH-')],
    [sg.Multiline('', size=(80,10), key='-RESULT-', autoscroll=True, disabled=True)]
]

window = sg.Window('MeetingAssistant Launcher', layout)

# Event loop
bot_process = None
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    # Launch Telegram bot in background
    if event == '-BOT-':
        try:
            # If already running, do nothing
            if bot_process is None or bot_process.poll() is not None:
                # Use Python executable to run the bot script
                if sys.platform.startswith('win'):
                    # On Windows, create a new process without a console
                    DETACHED = 0x00000008
                    bot_process = subprocess.Popen(
                        [sys.executable, os.path.join('modules','assistantbot.py')],
                        creationflags=DETACHED, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    # On Unix/macOS, start new session to detach
                    bot_process = subprocess.Popen(
                        [sys.executable, os.path.join('modules','assistantbot.py')],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                window['-LOG-'].print("Telegram bot launched.")
            else:
                window['-LOG-'].print("Telegram bot is already running.")
        except Exception as e:
            window['-LOG-'].print(f"Failed to launch bot: {e}")

    # Process selected file: transcribe and summarize
    if event == '-PROCESS-':
        file_path = values['-FILE-']
        title = values['-TITLE-'].strip() or os.path.splitext(os.path.basename(file_path))[0]
        if not file_path or not os.path.isfile(file_path):
            sg.popup_error("Please select a valid audio/video file.")
            continue
        # Create timestamped folder: meetings/YYYY/MM/DD-title/
        date = datetime.now().strftime('%Y/%m/%d')
        safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        meeting_folder = os.path.join('meetings', date + '-' + safe_title)
        os.makedirs(meeting_folder, exist_ok=True)
        
        window['-LOG-'].print(f"Processing file: {file_path}")
        try:
            # Copy source file for record
            shutil.copy(file_path, meeting_folder)
            # Transcribe and summarize
            transcript = transcription.transcribe(file_path)
            summary = summarization.summarize(transcript)
            # Save outputs
            with open(os.path.join(meeting_folder, 'transcript.txt'), 'w', encoding='utf-8') as f:
                f.write(transcript)
            with open(os.path.join(meeting_folder, 'summary.txt'), 'w', encoding='utf-8') as f:
                f.write(summary)
            window['-LOG-'].print("Transcription and summarization complete.")
        except Exception as e:
            window['-LOG-'].print(f"Error during processing: {e}")

    # Search previous meeting summaries
    if event == '-DOSEARCH-':
        query = values['-SEARCH-'].strip()
        if not query:
            sg.popup_error("Enter a search query.")
            continue
        try:
            results = search_module.search(query)
            # Assume results is a list of strings or single string
            if isinstance(results, list):
                window['-RESULT-'].update('\n\n'.join(results))
            else:
                window['-RESULT-'].update(results)
        except Exception as e:
            window['-RESULT-'].update(f"Search error: {e}")

window.close()
