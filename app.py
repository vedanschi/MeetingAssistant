import sys
sys.dont_write_bytecode = True 
import os
import sys
import shutil
import subprocess
import webbrowser
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

# Your existing imports
from modules.transcribe import transcribe
from modules.summarize import summarize
from modules.search import query_faiss, build_faiss_index

class MeetingAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MeetingAssistant")
        self.bot_proc = None
        self._create_widgets()

    def _create_widgets(self):
        # Telegram Bot Section
        bot_frame = ttk.LabelFrame(self, text="Telegram Bot")
        bot_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Button(bot_frame, text="Launch Bot", command=self.launch_bot).grid(row=0, column=0)
        link = ttk.Label(bot_frame, text="t.me/twenty_three_ventures_bot", foreground="blue", cursor="hand2")
        link.grid(row=0, column=1, padx=10)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/twenty_three_ventures_bot"))

        # File Processing Section
        file_frame = ttk.LabelFrame(self, text="Process Meeting")
        file_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.title_entry = ttk.Entry(file_frame, width=30)
        self.title_entry.grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        ttk.Button(file_frame, text="Process", command=self.process_file).grid(row=1, column=0, pady=5)

        # Log and Results
        self.log_area = scrolledtext.ScrolledText(self, width=80, height=10, state="disabled")
        self.log_area.grid(row=2, column=0, padx=10, pady=5)

        # Search Section
        search_frame = ttk.Frame(self)
        search_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.grid(row=0, column=0)
        ttk.Button(search_frame, text="Search", command=self.search).grid(row=0, column=1, padx=5)
        self.result_area = scrolledtext.ScrolledText(self, width=80, height=10, state="disabled")
        self.result_area.grid(row=4, column=0, padx=10, pady=5)

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state="disabled")
        self.log_area.see(tk.END)

    def launch_bot(self):
        try:
            if not self.bot_proc or self.bot_proc.poll() is not None:
                self.bot_proc = subprocess.Popen(
                    [sys.executable, "assistantbot.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                self.log("Telegram bot launched. Connect at:")
                self.log("👉 https://t.me/twenty_three_ventures_bot")
            else:
                self.log("Bot already running.")
        except Exception as e:
            self.log(f"Error launching bot: {e}")

    def browse_file(self):
        path = filedialog.askopenfilename(
            filetypes=(("Media Files", "*.wav;*.mp3;*.mp4"),)
        )
        if path:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, Path(path).stem)

    def process_file(self):
        path = self.title_entry.get()
        if not path or not Path(path).exists():
            messagebox.showerror("Error", "Select a valid file first.")
            return

        # ... (rest of your existing process_file logic, replacing `window['-LOG-'].print` with `self.log()`)

    def search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showinfo("Info", "Enter a search query.")
            return
        self.log(f"Searching for '{query}'...")
        results = query_faiss(query, k=5)
        # ... (update results area)

if __name__ == "__main__":
    app = MeetingAssistant()
    app.mainloop()