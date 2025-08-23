# app/services/solutions_service.py
from typing import List, Dict, Any, Optional
import chromadb
from functools import lru_cache
from app.services.vectorstore import get_store

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

from typing import List, Tuple

def _query_vector_store(query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    try:
        try:
            from app.services.vectorstore import get_store  # type: ignore
        except ImportError:
            from .vectorstore import get_store  # type: ignore

        store = get_store()
        try:
            res = store.query(query_texts=[query], n_results=top_k)
        except TypeError:
            res = store.query(query_texts=[query], k=top_k)

        docs_ll = res.get("documents") or res.get("docs") or [[]]
        docs = docs_ll[0] if isinstance(docs_ll, list) and docs_ll else []
        if docs is None:
            docs = []

        scores_ll = res.get("distances") or res.get("scores") or None
        if isinstance(scores_ll, list) and scores_ll:
            scores = scores_ll[0] or []
        else:
            scores = [0.0] * len(docs)

        if len(scores) < len(docs):
            scores += [0.0] * (len(docs) - len(scores))
        elif len(scores) > len(docs):
            scores = scores[:len(docs)]

        out: List[Tuple[str, float]] = []
        for d, s in zip(docs, scores):
            try:
                f = float(s)
            except Exception:
                f = 0.0
            out.append((str(d) if d is not None else "", f))

        return out[:top_k]
    except Exception:
        return []

def retrieve_solution(issue: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """
    Legacy API expected by enrichment fallback. Returns [(text, score), ...].
    """
    store = get_store()
    res = store.query(query_texts=[issue], n_results=top_k)
    docs = (res.get("documents") or [[]])[0] or []
    scores = (res.get("distances") or res.get("scores") or [[0.0]*len(docs)])[0]
    return list(zip(docs, scores))

def retrieve_top_solutions_robust(issue: str, top_k: int = 3) -> List[str]:
    """
    Newer API expected by enrichment.py top path. Returns [text, ...].
    """
    pairs = retrieve_solution(issue, top_k=top_k)
    return [t for (t, _s) in pairs]

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

def retrieve_top_solutions_filtered(issue: str, top_k: int = 3, max_distance: float = 0.6) -> list[str]:
    """
    Returns texts with distance <= max_distance (cosine distance).
    """
    store = get_store()
    res = store.query(query_texts=[issue], n_results=top_k*2)  # overfetch a bit
    docs = (res.get("documents") or [[]])[0] or []
    dists = (res.get("distances") or [[1.0]*len(docs)])[0] or []

    items = [(t, d) for t, d in zip(docs, dists) if t]
    items.sort(key=lambda x: x[1])  # smaller = better

    # keep only strong matches
    texts = []
    seen = set()
    for t, d in items:
        if d <= max_distance:
            k = t.strip()
            if k not in seen:
                seen.add(k)
                texts.append(k)
        if len(texts) >= top_k:
            break
    return texts

from typing import TypedDict, List
class EnrichmentResult(TypedDict):
    solutions: List[str]
    _force_change: bool
    method: str
