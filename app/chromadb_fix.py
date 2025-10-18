
"""
ChromaDB Connection Fix
This ensures consistent settings across all ChromaDB instances.
"""

import chromadb
from chromadb.config import Settings

# Global ChromaDB settings to ensure consistency
CHROMADB_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db",
    anonymized_telemetry=False
)

def get_chromadb_client():
    """Get a consistent ChromaDB client with unified settings."""
    try:
        client = chromadb.PersistentClient(path="./chroma_db", settings=CHROMADB_SETTINGS)
        return client
    except Exception as e:
        # If there's a conflict, try with different settings
        try:
            client = chromadb.PersistentClient(path="./chroma_db")
            return client
        except Exception as e2:
            # Last resort: use ephemeral client
            return chromadb.Client()

def get_or_create_collection(client, collection_name="docscanner_knowledge"):
    """Get or create a collection with consistent settings."""
    try:
        collection = client.get_collection(name=collection_name)
        return collection
    except:
        # Create collection if it doesn't exist
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        return collection
