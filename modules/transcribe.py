# modules/transcribe.py

import subprocess
from pathlib import Path

def transcribe(input_file: str, output_file: str) -> None:
    inp = Path(input_file).resolve()  # Convert to absolute path
    out = Path(output_file).resolve()

    # Ensure output directory exists
    out.parent.mkdir(parents=True, exist_ok=True)

# Remove .txt suffix for -of flag
    base_out = out.parent / out.stem  # e.g., "transcript" instead of "transcript.txt"

# Build whisper.cpp command
    whisper_cli = Path("whisper.cpp") / "build" / "bin" / "Release" / "whisper-cli.exe"
    model_bin = Path("models") / "ggml-base.en.bin"

    cmd = [
    str(whisper_cli),
    "--model", str(model_bin),
    "-of", str(base_out),  # Generates base_out.txt
    "-otxt",
    str(inp)
          ]
    subprocess.run(cmd, check=True)


    # Verify TXT file was created
    if not out.exists():
          raise FileNotFoundError(f"Transcript not generated at {out}")