# modules/summarize.py
from llama_cpp import Llama
import os

# Path to your downloaded GGUF model
MODEL_PATH = "models/orca-mini-3b-gguf2-q4_0.gguf"

def summarize(transcript_path: str, summary_path: str):
    """
    Loads the orca-mini model and summarizes the meeting transcript.
    """
    try:
    # Read transcript text
        text = open(transcript_path, encoding="utf-8").read()
    
        # Instantiate llama.cpp model
        llama = Llama(model_path=MODEL_PATH)
    
        # Build prompt for summarization
        prompt = (
            "You are a summarization assistant. "
            "Read the following meeting transcript and produce a concise bullet-point summary:\n\n"
            f"{text}\n\nSummary:\n-"
        )
    
        # Generate completion
        response = llama(
            prompt=prompt,
            max_tokens=256,          # adjust as needed
            stop=["\n\n"],           # stop after summary block
        )
    
        summary = response["choices"][0]["text"].strip()
    
        # Ensure output directory exists
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    
        # Write summary to file
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
    
        print(f"[✓] Summary saved to {summary_path}")
    except FileNotFoundError:
        raise RuntimeError("Transcript file not found.")
    except Exception as e:
        raise RuntimeError(f"Summarization failed: {e}")
