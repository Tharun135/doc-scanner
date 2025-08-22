# services/solutions_service.py
import chromadb
from functools import lru_cache
from typing import Optional, Dict, Any

CHROMA_PATH = "./chroma_db"               # <- change to absolute path if needed
COLLECTION = "docscanner_solutions"

@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection(COLLECTION)

def get_solution(issue_text: str, issue_type_hint: Optional[str] = None, top_k: int = 1) -> Optional[Dict[str, Any]]:
    col = _get_collection()
    res = col.query(query_texts=[issue_text], n_results=max(3, top_k))
    # Prefer hits matching the hint (if provided)
    if issue_type_hint and res.get("metadatas") and res["metadatas"][0]:
        keep = [
            i for i, meta in enumerate(res["metadatas"][0])
            if issue_type_hint.lower() in meta.get("issue_type", "").lower()
        ]
        if keep:
            res = {
                "ids": [[res["ids"][0][i] for i in keep]],
                "documents": [[res["documents"][0][i] for i in keep]],
                "metadatas": [[res["metadatas"][0][i] for i in keep]],
            }

    if not res.get("documents") or not res["documents"][0]:
        return None

    doc = res["documents"][0][0]           # contains Solution + Why + References (we ingested them together)
    meta = res["metadatas"][0][0]          # {"rule_id","issue_type","explanation","reference",...}
    return {"text": doc, "meta": meta}
