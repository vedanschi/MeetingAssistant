# modules/embed.py
from sentence_transformers import SentenceTransformer

# Use a small, fast model
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

def load_embedder():
    """Return a SentenceTransformer instance for embedding texts."""
    return SentenceTransformer(EMBED_MODEL_NAME)
