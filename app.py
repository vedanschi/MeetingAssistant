import PySimpleGUI as sg
import subprocess, os
from modules.transcribe import transcribe
from modules.summarize  import summarize
from modules.search import build_faiss_index, query_faiss


# 1️⃣ Define the window layout
layout = [
    [sg.Text("Meeting Assistant")],
    [sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("Audio/Video", "*.wav;*.mp4"), ("All", "*.*")))],
    [sg.Button("Process"), sg.Button("Search Index"), sg.Exit()],
    [sg.Text("Query:"), sg.Input(key="-SEARCH-"), sg.Button("Search")],
    [sg.Multiline(size=(70, 10), key="-RESULTS-")],
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

    # Step 1: Parse the query for keywords (dates, actions, topics)
    sg.popup("Parsing query...")
    keywords = extract_keywords(query_text)

    # Display parsed keywords
    date_text = ", ".join(keywords["dates"]) if keywords["dates"] else "No date found."
    action_text = ", ".join(keywords["actions"]) if keywords["actions"] else "No actions found."
    topic_text = ", ".join(keywords["topics"]) if keywords["topics"] else "No topics found."

    result_text = f"Dates: {date_text}\nActions: {action_text}\nTopics: {topic_text}"

    # Update the result panel with parsed query information
    window["-RESULTS-"].update(result_text)

    # Step 2: Perform FAISS search
    sg.popup("Searching…")
    results = query_faiss(query_text, k=5)
    if not results:
        window["-RESULTS-"].update("No matching meetings found.")
    else:
        # Build a display string for FAISS results
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

        # 🧠 Build FAISS index after summarization
        sg.popup("Updating search index…")
        build_faiss_index()

        sg.popup(f"Done!\nTranscript: {txt}\nSummary: {summ}")

window.close()
