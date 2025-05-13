# MeetingAssistant

[![PyPI version](https://img.shields.io/pypi/v/MeetingAssistant.svg)](https://pypi.org/project/MeetingAssistant/)
[![Python Version](https://img.shields.io/pypi/pyversions/MeetingAssistant)](https://pypi.org/project/MeetingAssistant/)

**MeetingAssistant** is a **local-first** conversational meeting assistant that you run on your own computer. It lets you upload audio/video recordings and automatically transcribes, summarizes, and organizes your meetings. All processing happens locally using state-of-the-art AI models - your data never leaves your device.

![MeetingAssistant Demo](images/demo.gif)

## Key Features

- 🎙️ **Local Transcription** - Whisper.cpp-based speech-to-text
- 📝 **AI Summarization** - DistilBART-CNN-12-6 model for concise summaries
- 🔍 **Semantic Search** - FAISS-powered meeting content retrieval
- 🤖 **Multi-Interface** - Desktop GUI + Telegram bot
- 🔒 **Privacy-First** - No cloud services or external APIs
- 🚀 **CPU/GPU Support** - Runs efficiently on both processors

## Installation

### Quick Install (PyPI)
```bash
pip install MeetingAssistant==0.1.1

### Screenshots / Demo

*Screenshots/Demo GIFs coming soon. Placeholder images below.*

* ![MeetingAssistant Desktop GUI screenshot (placeholder)]() *Desktop app showing transcript and summary (placeholder)*.
* ![MeetingAssistant Telegram bot screenshot (placeholder)]() *Telegram bot interface (placeholder)*.

### Full Setup
Install System Dependencies

bash
# Windows
winget install -e --id Kitware.CMake
Build Whisper.cpp

bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp && mkdir build && cd build
cmake .. && cmake --build . --config Release
Download Models

bash
# Whisper base.en model
curl -LO https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

# Move models to project directory
mkdir -p ~/.MeetingAssistant/models
mv ggml-base.en.bin ~/.MeetingAssistant/models/
Set Up Telegram Bot (Optional)

bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
Usage
Desktop GUI
bash
meeting-assistant gui
Desktop Interface

Telegram Bot
bash
meeting-assistant telegram
Telegram Interface

Command Line
bash
# Process a meeting file
meeting-assistant process meeting.mp4

# Search previous meetings
meeting-assistant search "project timeline"
Advanced Configuration
Folder Structure
~/.MeetingAssistant/
├── models/
│   ├── ggml-base.en.bin       # Whisper model
├── meetings/
│   ├── 2024-01-15-client-call/
│   │   ├── recording.mp4
│   │   ├── transcript.txt
│   │   └── summary.txt

### Environment Variables
bash
# Custom model paths
export WHISPER_MODEL_PATH="~/custom_models/ggml-large-v3.bin"

### Disable Telegram bot
export DISABLE_TELEGRAM=1
Development
bash
git clone https://github.com/vedanschi/MeetingAssistant.git
cd MeetingAssistant
pip install -e .

### License
MIT License - See LICENSE for details

This project is licensed under the [MIT License](LICENSE). All code, documentation, and data formats are available under MIT terms.

**Acknowledgments:** MeetingAssistant leverages [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for fast transcription, [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for running the local LLM, and [FAISS](https://github.com/facebookresearch/faiss) for semantic search indexing. These powerful open-source components enable MeetingAssistant to operate entirely offline.
