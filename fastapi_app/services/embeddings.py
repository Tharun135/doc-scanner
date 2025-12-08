# fastapi_app/services/embeddings.py
"""
Embedding generation service supporting multiple backends:
- SentenceTransformers (local)
- Ollama (local)
- OpenAI (cloud)
"""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Unified interface for generating embeddings from multiple providers.
    Supports local SentenceTransformers and Ollama models.
    """
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_ollama: bool = False,
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "nomic-embed-text"
    ):
        self.use_ollama = use_ollama
        self.model_name = model_name
        
        if use_ollama:
            self.ollama_url = ollama_url
            self.ollama_model = ollama_model
            self.model = None
            logger.info(f"Using Ollama embeddings: {ollama_model} at {ollama_url}")
        else:
            logger.info(f"Loading SentenceTransformer model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info(f"Model loaded successfully. Dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed_texts(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of text strings to embed
            show_progress: Show progress bar for batch processing
            
        Returns:
            List of embedding vectors (each a list of floats)
        """
        if not texts:
            return []
        
        if self.use_ollama:
            return self._embed_with_ollama(texts)
        
        # Use SentenceTransformers
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            batch_size=32  # Process in batches for efficiency
        )
        
        # Convert numpy arrays to lists
        return [emb.tolist() for emb in embeddings]
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty")
        
        embeddings = self.embed_texts([text], show_progress=False)
        return embeddings[0]
    
    def _embed_with_ollama(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama API."""
        try:
            import requests
            embeddings = []
            
            for text in texts:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.ollama_model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                embedding = response.json()["embedding"]
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings with Ollama: {e}")
    
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        if self.use_ollama:
            # Test with a dummy text to get dimension
            test_emb = self.embed_query("test")
            return len(test_emb)
        return self.model.get_sentence_embedding_dimension()
    
    def batch_embed(
        self, 
        texts: List[str], 
        batch_size: int = 64
    ) -> List[List[float]]:
        """
        Embed texts in batches for better performance.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embed_texts(batch, show_progress=True)
            all_embeddings.extend(batch_embeddings)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return all_embeddings


# Singleton instance (will be initialized by dependency injection in main.py)
_embedder: Optional[EmbeddingModel] = None


def get_embedder(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    use_ollama: bool = False,
    ollama_url: str = "http://localhost:11434",
    ollama_model: str = "nomic-embed-text"
) -> EmbeddingModel:
    """
    Get or create the global embedder instance.
    Thread-safe singleton pattern.
    """
    global _embedder
    
    if _embedder is None:
        _embedder = EmbeddingModel(
            model_name=model_name,
            use_ollama=use_ollama,
            ollama_url=ollama_url,
            ollama_model=ollama_model
        )
    
    return _embedder
