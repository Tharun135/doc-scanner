# app/services/vectorstore.py
import os
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

# Config defaults (can override via env vars)
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "docscanner_rules")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

_client: ClientAPI | None = None
_collection: Collection | None = None


def _get_embedding_function():
    return embedding_functions.OllamaEmbeddingFunction(
        url=OLLAMA_URL,
        model_name=OLLAMA_EMBED_MODEL,
    )


def get_store() -> Collection:
    """
    Return a Chroma collection handle with an embedding function attached.
    """
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = _get_embedding_function()

    col = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    _collection = col
    return _collection

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
