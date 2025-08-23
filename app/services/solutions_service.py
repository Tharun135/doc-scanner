# app/services/solutions_service.py
from typing import List, Dict, Any, Optional
import chromadb
from functools import lru_cache

CHROMA_PATH = "./chroma_db"
COLLECTION = "docscanner_solutions"
MIN_SIMILARITY = 0.60     # tweak as needed

@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        return client.get_collection(COLLECTION)
    except Exception:
        return None

def _similarity_from_distance(distance: Optional[float]) -> float:
    if distance is None:
        return 0.0
    # For Chroma default (L2), smaller distance = more similar.
    # Map roughly to [0..1] similarity (simple heuristic).
    return max(0.0, 1.0 - min(distance, 1.0))

def retrieve_top_solutions(query_text: str, issue_type_hint: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
    col = _get_collection()
    if not col or not query_text:
        return []
    try:
        results = col.query(
            query_texts=[f"{issue_type_hint} :: {query_text}".strip(" :")],
            n_results=top_k,
            include=["metadatas", "documents", "distances", "ids"]
        )
        hits = []
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        docs = results.get("documents", [[]])[0] if results.get("documents") else []
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        dists = results.get("distances", [[]])[0] if results.get("distances") else []
        for i, mid in enumerate(ids):
            sim = _similarity_from_distance(dists[i] if i < len(dists) else None)
            hits.append({
                "id": mid,
                "similarity": sim,
                "document": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
            })
        # keep only strong enough hits
        hits = [h for h in hits if h["similarity"] >= MIN_SIMILARITY]
        # sort by similarity desc
        hits.sort(key=lambda x: x["similarity"], reverse=True)
        return hits
    except Exception:
        return []
