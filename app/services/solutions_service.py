# services/solutions_service.py
import chromadb
from functools import lru_cache
from typing import Optional, Dict, Any
import os

# Make path robust regardless of where the app runs from
ROOT = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.abspath(os.path.join(ROOT, "..", "chroma_db"))
COLLECTION = "docscanner_solutions"

@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        return client.get_collection(COLLECTION)
    except Exception:
        return None  # collection not found, fail gracefully

def retrieve_solution(issue_text: str, issue_type_hint: Optional[str] = None, top_k: int = 1) -> Optional[Dict[str, Any]]:
    col = _get_collection()
    if col is None:
        return None  # just skip if no collection

    res = col.query(query_texts=[issue_text], n_results=max(3, top_k))

    # Prefer hits that match issue_type if provided
    if issue_type_hint and res.get("metadatas") and res["metadatas"][0]:
        keep = [
            i for i, meta in enumerate(res["metadatas"][0])
            if issue_type_hint.lower() in (meta.get("issue_type", "")).lower()
        ]
        if keep:
            res = {
                "ids": [[res["ids"][0][i] for i in keep]],
                "documents": [[res["documents"][0][i] for i in keep]],
                "metadatas": [[res["metadatas"][0][i] for i in keep]],
            }

    if not res.get("documents") or not res["documents"][0]:
        return None

    return {
        "text": res["documents"][0][0],
        "meta": res["metadatas"][0][0],
    }
