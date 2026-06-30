# app/services/vectorstore.py
import os

# Config defaults
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "docscanner_rules")

def get_store():
    """Dummy method since we are not using ChromaDB anymore"""
    return None

def upsert_rules(items: list[dict]):
    pass

def clear_collection():
    pass

# ---------- Optional helpers (nice to have) ----------

def upsert_rules(items: list[dict]):
    """
    Upsert a list of rules/snippets into the collection.
    Each item should be shaped like:
      { "id": "unique-id", "text": "content to embed", "metadata": {"tag": "style"} }
    """
    if not items:
        return

    store = get_store()
    ids, docs, metas = [], [], []
    for it in items:
        ids.append(str(it["id"]))
        docs.append(str(it["text"]))
        metas.append(it.get("metadata") or {})

    store.upsert(ids=ids, documents=docs, metadatas=metas)


def clear_collection():
    """
    Danger: wipes the collection.
    """
    client = _get_client()
    client.delete_collection(CHROMA_COLLECTION)
