import os
import pickle
from pathlib import Path
from datetime import datetime
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("index")
INDEX_PATH = INDEX_DIR / "faiss.index"
META_PATH = INDEX_DIR / "metadata.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBED_MODEL)

def build_faiss_index():
    """Build search index with proper date parsing and deduplication"""
    INDEX_DIR.mkdir(exist_ok=True)
    docs, metas = [], []

    for summ in Path("meetings").rglob("summary.txt"):
        try:
            parts = summ.parts
            if len(parts) < 4:
                continue  # Skip invalid paths

            # Parse date from directory structure
            year, month, day_slug = parts[1], parts[2], parts[3]
            day = day_slug.split("-", 1)[0]
            
            # Read summary content
            content = summ.read_text(encoding="utf-8").strip()
            if not content:
                continue

            # Create unique meeting ID
            meeting_id = f"{year}-{month}-{day}-{summ.parent.name}"
            
            metas.append({
                "id": meeting_id,
                "date": datetime(int(year), int(month), int(day)).isoformat(),
                "year": year,
                "month": month,
                "day": day,
                "slug": summ.parent.name,
                "content": content,
                "path": str(summ)
            })
            docs.append(content)
            
        except (ValueError, IndexError) as e:
            print(f"Skipping invalid file {summ}: {e}")
            continue

    if not docs:
        raise RuntimeError("No valid summaries found in meetings directory")

    # Create FAISS index
    embs = embedder.encode(docs, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embs.shape[1])
    index.add(embs)
    
    # Save index and metadata
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "wb") as f:
        pickle.dump(metas, f)

    print(f"Indexed {len(docs)} meetings with {embs.shape[1]}D embeddings")

def query_faiss(query: str, k: int = 5) -> list[dict]:
    """Search with date filtering and proper deduplication"""
    if not INDEX_PATH.exists():
        raise FileNotFoundError("Index not found - run build_faiss_index() first")

    # Load index and metadata
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "rb") as f:
        metas = pickle.load(f)

    # Encode query and search
    query_emb = embedder.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_emb, k)

    # Process results with deduplication
    seen = set()
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= len(metas):
            continue
            
        entry = metas[idx].copy()
        entry["score"] = float(dist)
        
        # Deduplicate by meeting ID
        if entry["id"] not in seen:
            seen.add(entry["id"])
            results.append(entry)
            
        if len(results) >= k:
            break

    # Sort by date descending
    return sorted(
        results,
        key=lambda x: x["date"],
        reverse=True
    )[:k]
