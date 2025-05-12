# modules/summarize.py
from transformers import pipeline
from pathlib import Path
import logging

# Load model once at startup
SUMMARIZER = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    tokenizer="sshleifer/distilbart-cnn-12-6"
)

    
def summarize(transcript_path: str, summary_path: str):
    try:
        transcript = Path(transcript_path).read_text(encoding="utf-8")
        
        # Truncate to model's max input length (1024 tokens)
        truncated = transcript[:3000]  # ~500 words
        
        summary = SUMMARIZER(
            truncated,
            max_length=150,
            min_length=30,
            do_sample=False
        )[0]['summary_text']

        Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
        Path(summary_path).write_text(summary, encoding="utf-8")
        logging.info(f"Summary saved to {summary_path}")

    except Exception as e:
        logging.error(f"Summarization failed: {e}")
        raise RuntimeError(f"Summarization error: {e}")