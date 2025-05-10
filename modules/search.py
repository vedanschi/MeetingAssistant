import faiss
import os
import pickle
from pathlib import Path
from modules.embed import load_embedder


INDEX_PATH = "index/faiss.index"
META_PATH = "index/metadata.pkl"


embedder = load_embedder()

def build_faiss_index(meeting_base="meetings"):
    """
    Walk through all meeting summaries and build a FAISS index.
    Stores vectors and metadata.
    """
    documents = []
    metadata = []
    
    for root, _, files in os.walk(meeting_base):
        for file in files:
            if file == "summary.txt":
                file_path = Path(root)/file
                with open(file_path, encoding="utf-8") as f:
                    text = f.read()
                documents.append(text)
                metadata.append({
                    "path": str(file_path),
                    "year": file_path.parts[1],
                    "month": file_path.parts[2],
                    "slug": file_path.parts[3],
                })

   
    vectors = embedder.encode(documents)

    
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

  
    os.makedirs("index", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[✓] Indexed {len(documents)} summaries.")


def query_faiss(query, k=5):
    """
    Query the FAISS index for top-k similar summaries.
    Returns metadata with similarity scores.
    """
    if not Path(INDEX_PATH).exists() or not Path(META_PATH).exists():
        raise FileNotFoundError("FAISS index not found. Run build_faiss_index() first.")

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)

    query_vec = embedder.encode([query])
    D, I = index.search(query_vec, k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < len(metadata):
            result = metadata[idx]
            result["score"] = float(score)
            results.append(result)

    return results
