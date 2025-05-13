# modules/transcribe.py
import subprocess

def transcribe(input_path: str, output_txt: str):
    """
    Runs whisper-cli on input_path, saving transcript to output_txt.
    """
    try:
        cmd = [
            "../whisper.cpp/build/bin/whisper-cli",
            "--model", "../models/ggml-base.en.bin",
            "--output", output_txt,
            input_path
        ]
        subprocess.run(cmd, check=True)
        print(f"[✓] Transcript saved to {output_txt}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Transcription failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during transcription: {e}")
