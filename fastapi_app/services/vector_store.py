# fastapi_app/services/vector_store.py
"""
ChromaDB vector store manager with full CRUD operations.
Handles document chunk storage and semantic search.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChromaManager:
    """
    Manager for ChromaDB vector store operations.
    Provides methods for storing and querying document chunks.
    """
    
    def __init__(
        self, 
        persist_directory: str = "./chroma_db",
        collection_name: str = "doc_chunks"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Collection '{collection_name}' ready. Item count: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise
    
    def add_chunks(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Add document chunks to the vector store.
        
        Args:
            ids: Unique identifiers for each chunk
            texts: The text content of each chunk
            embeddings: Embedding vectors for each chunk
            metadatas: Metadata dictionaries for each chunk
        """
        if not ids or len(ids) != len(texts) != len(embeddings) != len(metadatas):
            raise ValueError("All input lists must have the same non-zero length")
        
        try:
            logger.info(f"Adding {len(ids)} chunks to collection '{self.collection_name}'")
            
            # ChromaDB add operation (upserts by default)
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(ids)} chunks. Total items: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise
    
    def upsert_chunks(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Upsert (update or insert) document chunks.
        
        Args:
            ids: Unique identifiers for each chunk
            texts: The text content of each chunk
            embeddings: Embedding vectors for each chunk
            metadatas: Metadata dictionaries for each chunk
        """
        if not ids or len(ids) != len(texts) != len(embeddings) != len(metadatas):
            raise ValueError("All input lists must have the same non-zero length")
        
        try:
            logger.info(f"Upserting {len(ids)} chunks to collection '{self.collection_name}'")
            
            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully upserted {len(ids)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store with a query embedding.
        
        Args:
            query_embedding: The embedding vector for the query
            top_k: Number of results to return
            where: Metadata filter (e.g., {"source": "manual.pdf"})
            where_document: Document content filter
            
        Returns:
            Dictionary with keys: ids, documents, metadatas, distances
        """
        try:
            logger.debug(f"Querying collection with top_k={top_k}")
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                where_document=where_document,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Flatten the results (query returns list of lists)
            return {
                'ids': results['ids'][0] if results['ids'] else [],
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def query_by_text(
        self,
        query_texts: List[str],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query using text (ChromaDB will handle embedding internally).
        Note: Requires collection to have an embedding function set.
        
        Args:
            query_texts: List of query text strings
            top_k: Number of results per query
            where: Metadata filter
            
        Returns:
            Dictionary with query results
        """
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=top_k,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Text query failed: {e}")
            raise
    
    def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """
        Retrieve chunks by their IDs.
        
        Args:
            ids: List of chunk IDs to retrieve
            
        Returns:
            Dictionary with documents and metadatas
        """
        try:
            results = self.collection.get(
                ids=ids,
                include=['documents', 'metadatas']
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get chunks by IDs: {e}")
            raise
    
    def delete_by_ids(self, ids: List[str]) -> None:
        """
        Delete chunks by their IDs.
        
        Args:
            ids: List of chunk IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} chunks")
        except Exception as e:
            logger.error(f"Failed to delete chunks: {e}")
            raise
    
    def delete_by_source(self, source: str) -> None:
        """
        Delete all chunks from a specific source document.
        
        Args:
            source: The source identifier (e.g., filename)
        """
        try:
            self.collection.delete(where={"source": source})
            logger.info(f"Deleted all chunks from source: {source}")
        except Exception as e:
            logger.error(f"Failed to delete chunks by source: {e}")
            raise
    
    def count(self) -> int:
        """Get total number of chunks in the collection."""
        return self.collection.count()
    
    def clear_collection(self) -> None:
        """Delete all items from the collection. Use with caution!"""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.warning(f"Collection '{self.collection_name}' cleared")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample of metadata to understand structure
            sample = None
            if count > 0:
                sample = self.collection.get(limit=1, include=['metadatas'])
            
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "persist_directory": self.persist_directory,
                "sample_metadata": sample['metadatas'][0] if sample and sample['metadatas'] else None,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Singleton instance
_vector_store: Optional[ChromaManager] = None


def get_vector_store(
    persist_directory: str = "./chroma_db",
    collection_name: str = "doc_chunks"
) -> ChromaManager:
    """
    Get or create the global vector store instance.
    Thread-safe singleton pattern.
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = ChromaManager(
            persist_directory=persist_directory,
            collection_name=collection_name
        )
    
    return _vector_store
