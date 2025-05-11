# MeetingAssistant

**MeetingAssistant** is a **local-first** conversational meeting assistant that you run on your own computer. It lets you upload audio or video recordings of meetings and automatically transcribes and summarizes them. All processing happens locally – the primary copy of your data lives on your device – so your recordings and notes never leave your control. Internally, MeetingAssistant uses [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (a C/C++ port of OpenAI’s Whisper) to transcribe speech to text, and a local LLM (Orca-mini 3B via llama-cpp-python) to generate concise summaries. Transcripts and summaries are stored in a structured folder for easy reference. The app also builds a semantic index of all meeting summaries using [FAISS](https://github.com/facebookresearch/faiss) – *“a library for efficient similarity search and clustering of dense vectors”* – so you can quickly search past meetings by topic or keywords. You can interact with MeetingAssistant through a simple desktop GUI (built with PySimpleGUI) or via a Telegram bot on your phone or desktop.

## Features

* **Local transcription:** Upload any meeting audio or video file; it is transcribed to text offline using Whisper.cpp.
* **Automated summaries:** Transcripts are summarized by a small local language model (Orca-mini 3B), producing a concise meeting summary.
* **Semantic search:** All meeting summaries are indexed with FAISS for fast semantic search – find relevant past meetings by typing natural-language queries.
* **Local-first storage:** Everything (audio, transcripts, summaries) is stored on your machine. No cloud services or external APIs are used, preserving your privacy.
* **Desktop GUI:** A user-friendly desktop app (PySimpleGUI) lets you manage meetings, run transcriptions/summaries, and chat with the assistant.
* **Telegram bot:** A Telegram bot interface lets you send voice notes or commands to the assistant from any device.
* **Easy deployment:** Runs entirely on CPU or GPU (if available) without requiring internet access.

### Screenshots / Demo

*Screenshots/Demo GIFs coming soon. Placeholder images below.*

* ![MeetingAssistant Desktop GUI screenshot (placeholder)]() *Desktop app showing transcript and summary (placeholder)*.
* ![MeetingAssistant Telegram bot screenshot (placeholder)]() *Telegram bot interface (placeholder)*.

## Installation

Follow these steps to set up MeetingAssistant:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/vedanschi/MeetingAssistant.git
   cd MeetingAssistant
   ```

2. **Install Python dependencies:**

   ```bash
   python3 -m pip install -r requirements.txt
   ```

   This installs needed libraries (PySimpleGUI, `llama-cpp-python`, FAISS, Telegram bot libs, etc).

3. **Build Whisper.cpp:**
   MeetingAssistant uses [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for transcription. Clone and build it:

   ```bash
   git clone https://github.com/ggerganov/whisper.cpp.git
   cd whisper.cpp
   make
   ```

   This produces the `whisper.cpp` binary. You may also install any required BLAS libraries for better performance (see the whisper.cpp [README](https://github.com/ggerganov/whisper.cpp) for details).

4. **Download Whisper models:**
   By default, whisper.cpp requires GGML-format models. Download a model (e.g. **base.en**, **small**, etc) using the whisper.cpp `make` scripts:

   ```bash
   make base.en  # downloads and converts base English model
   ```

   Copy the downloaded model file (e.g. `models/ggml-base.en.bin`) into the MeetingAssistant project directory or specify its path in the app when prompted.

5. **Download the LLM model:**
   MeetingAssistant uses a quantized LLaMA model (orca-mini-3b-gguf2-q4\_0). You can obtain this model from the [GPT4All model zoo](https://gpt4all.io/models/). Download the **orca-mini-3b-gguf2-q4\_0** model file and place it in the `models/` folder of the project (create this folder if it doesn’t exist). Ensure the filename matches what the app expects (e.g. `models/orca-mini-3b.gguf`).

6. **Set up Telegram (optional):**
   If you want to use the Telegram bot, create a new bot via [BotFather](https://t.me/BotFather) to get a **Bot API token**. Then set an environment variable for it:

   ```bash
   export TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_API_TOKEN"
   ```

   Alternatively, you can edit the bot token into a config file as instructed in the code.

7. **Verify folder structure:**
   The project expects a directory structure roughly like:

   ```
   MeetingAssistant/
   ├─ app.py                 # Main app script
   ├─ requirements.txt
   ├─ models/               # Place Whisper & LLM models here
   │    └─ orca-mini-3b.gguf
   ├─ meetings/             # (Auto-created) stores transcripts and summaries
   └─ modules/              # Python modules (audio processing, summarization, etc)
   ```

   The `build/` folder and `23VenturesAssistant.spec` are used for packaging (see below) and can be ignored during setup.

## Usage

### Desktop App (GUI)

1. **Launch the app:** In your environment with Python and the models set up, run:

   ```bash
   python app.py
   ```

   This opens the MeetingAssistant desktop window.

2. **Uploading a meeting:** In the GUI, use the *“Upload”* button to select an audio (e.g. `.wav`, `.mp3`) or video file. The app will start transcribing it with Whisper.cpp. Progress and transcript text will appear in the window.

3. **Generate summary:** After transcription, click *“Summarize”*. The local LLM (Orca-mini) will read the transcript and produce a summary. This summary is displayed alongside the transcript.

4. **Search & Chat:** The GUI also includes a chat interface. You can type or speak queries (e.g. “Show me next week’s action items” or “Search for budget discussion”). The assistant will search the indexed meeting summaries (using FAISS) and respond with relevant information.

5. **Access saved data:** All meetings, transcripts, and summaries are saved under the `meetings/` folder in timestamped subfolders. You can browse or edit these files directly if needed.

### Telegram Bot

1. **Start the bot:** With `TELEGRAM_BOT_TOKEN` set, run the Telegram bot script (for example):

   ```bash
   python modules/telegram_bot.py
   ```

   (Adjust the path if your project structure differs.)

2. **Interact with the bot:** In Telegram, find your bot by its username and start a chat. You can send:

   * **Voice messages or audio files:** The bot will reply with a transcription and summary of the audio, using Whisper.cpp and the LLM, all running locally.
   * **Text messages:** Ask questions about past meetings (e.g. “What were the conclusions of last week’s meeting?”). The bot will use FAISS search to find relevant summaries and reply accordingly.
   * **Commands:** You may implement or use existing commands (like `/new` to upload a file). Refer to the bot’s help or source code for available commands.

   All interactions and resulting transcripts/summaries are stored in the same `meetings/` archive on your machine.

### CLI (Optional)

* There is no dedicated command-line tool by default, but you can script or use the Python modules directly. For example:

  ```bash
  python app.py --help
  ```

  may list available options (if implemented). You can also import modules (e.g. `transcribe`, `summarize`, `search`) in a Python REPL to process files or queries programmatically.

## Folder Structure

The main components of the repository are:

* `app.py` — **Main application script.** Starts the GUI (or runs in other modes).
* `modules/` — **Python modules** containing the core functionality (transcription, summarization, indexing, etc).
* `models/` — **Model files.** Place your Whisper and LLM model files here. (This folder is usually empty in the repo; you add models during setup.)
* `meetings/` — **Meeting data.** When you process files, this folder is populated with subfolders for each meeting, containing the original media (if saved), transcript text, and summary text.
* `build/` — **Build artifacts.** Contains files for packaging (such as a PyInstaller spec `23VenturesAssistant.spec`). You can use these to create standalone executables, but this is optional.
* `requirements.txt` — **Python dependencies.** Use `pip install -r requirements.txt` to install all needed libraries.
* `.gitignore` — Ignored files (e.g. model binaries) when committing to version control.
* `LICENSE` — Project license (MIT).

Each Python module (`modules/`) contains functions for a particular task (e.g. `transcribe.py`, `summarize.py`, `search.py`, etc). You do not normally need to run these individually; they are orchestrated by `app.py`. Review the code in `modules/` for details on how the processing pipeline works.

## Contributing

Contributions are welcome! If you find bugs or have feature suggestions, please open an issue. To contribute code, fork the repository and submit a pull request. We recommend following these guidelines:

* Ensure code is clean and well-documented.
* Write clear commit messages and include test cases where possible.
* By contributing, you agree that your work will be licensed under the MIT License.

This is an open-source project; please feel free to suggest improvements or extensions (e.g. support for more file formats, new summarization models, additional languages, etc).

## License

This project is licensed under the [MIT License](LICENSE). All code, documentation, and data formats are available under MIT terms.

**Acknowledgments:** MeetingAssistant leverages [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for fast transcription, [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for running the local LLM, and [FAISS](https://github.com/facebookresearch/faiss) for semantic search indexing. These powerful open-source components enable MeetingAssistant to operate entirely offline.
