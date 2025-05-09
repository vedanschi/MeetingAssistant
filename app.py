import PySimpleGUI as sg
import subprocess, os
from modules.transcribe import transcribe
from modules.summarize  import summarize

# 1️⃣ Define the window layout
layout = [
    [sg.Text("Meeting Assistant")],
    [sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("Audio/Video","*.wav;*.mp4"),("All","*.*")))],
    [sg.Button("Process"), sg.Exit()]
]

# 2️⃣ Create the window
window = sg.Window("23 Ventures Assistant", layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break


    if event == "Search":
        query_text = values["-SEARCH-"].strip()
        if not query_text:
            sg.popup("Please enter a search query.")
            continue

        sg.popup("Searching…")
        results = query_faiss(query_text, k=5)
        if not results:
            window["-RESULTS-"].update("No matching meetings found.")
        else:
            # Build a display string
            text = ""
            for r in results:
                date = f"{r['year']}-{r['month']}-{r['slug']}"
                text += f"{date}  (score: {r['score']:.2f})\n"
            window["-RESULTS-"].update(text)

    if event == "Process":
        raw_path = values["-FILE-"]
        if not raw_path:
            sg.popup("Please select a file first.")
            continue

        # Compute storage paths
        from datetime import date
        from pathlib   import Path
        today = date.today()
        slug  = Path(raw_path).stem
        base  = Path("meetings")/f"{today.year}"/f"{today:%m}"/f"{today:%d}-{slug}"
        raw_dst = base/Path(raw_path).name
        txt     = base/"transcript.txt"
        summ    = base/"summary.txt"
        os.makedirs(base, exist_ok=True)

        # Copy raw file
        sg.popup("Copying file…")
        subprocess.run(["cp", raw_path, str(raw_dst)])

        # Transcribe
        sg.popup("Transcribing…")
        transcribe(str(raw_dst), str(txt))

        # Summarize
        sg.popup("Summarizing…")
        summarize(str(txt), str(summ))

        sg.popup(f"Done!\nTranscript: {txt}\nSummary: {summ}")

window.close()
