# enhanced_rag/advanced_embeddings.py
"""
Advanced embedding system implementing high-quality embeddings with domain semantics.
Supports multiple embedding models including OpenAI, Cohere, and offline alternatives.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Union
import numpy as np
from functools import lru_cache
import json
import hashlib

# Try to import different embedding providers
EMBEDDING_PROVIDERS = {
    'openai': False,
    'cohere': False,
    'sentence_transformers': False,
    'ollama': False
}

try:
    import openai
    EMBEDDING_PROVIDERS['openai'] = True
except ImportError:
    pass

try:
    import cohere
    EMBEDDING_PROVIDERS['cohere'] = True
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_PROVIDERS['sentence_transformers'] = True
except ImportError:
    pass

try:
    import requests
    EMBEDDING_PROVIDERS['ollama'] = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


class AdvancedEmbeddingManager:
    """
    Advanced embedding manager supporting multiple high-quality embedding models.
    Implements domain-specific embedding strategies and caching for performance.
    """
    
    def __init__(self, 
                 provider: str = "auto",
                 model_name: Optional[str] = None,
                 cache_size: int = 10000,
                 batch_size: int = 100):
        """
        Initialize advanced embedding manager.
        
        Args:
            provider: Embedding provider ('openai', 'cohere', 'sentence_transformers', 'ollama', 'auto')
            model_name: Specific model name (provider-dependent)
            cache_size: Size of embedding cache
            batch_size: Batch size for processing multiple texts
        """
        self.provider = provider
        self.model_name = model_name
        self.cache_size = cache_size
        self.batch_size = batch_size
        self.embedding_cache = {}
        self.client = None
        self.model = None
        
        # Auto-select best available provider if needed
        if provider == "auto":
            self.provider = self._select_best_provider()
        
        # Initialize the selected provider
        self._initialize_provider()
        
        logger.info(f"✅ Advanced embedding manager initialized with {self.provider}")
    
    def _select_best_provider(self) -> str:
        """
        Automatically select the best available embedding provider.
        Priority: OpenAI > Cohere > SentenceTransformers > Ollama
        """
        if EMBEDDING_PROVIDERS['openai'] and os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif EMBEDDING_PROVIDERS['cohere'] and os.getenv('COHERE_API_KEY'):
            return 'cohere'
        elif EMBEDDING_PROVIDERS['sentence_transformers']:
            return 'sentence_transformers'
        elif EMBEDDING_PROVIDERS['ollama']:
            return 'ollama'
        else:
            raise RuntimeError("No embedding providers available. Install openai, cohere, sentence-transformers, or ensure ollama is running.")
    
    def _initialize_provider(self):
        """Initialize the selected embedding provider."""
        try:
            if self.provider == 'openai':
                self._initialize_openai()
            elif self.provider == 'cohere':
                self._initialize_cohere()
            elif self.provider == 'sentence_transformers':
                self._initialize_sentence_transformers()
            elif self.provider == 'ollama':
                self._initialize_ollama()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.provider}: {e}")
            # Fallback to next available provider
            available_providers = [p for p, available in EMBEDDING_PROVIDERS.items() if available and p != self.provider]
            if available_providers:
                logger.info(f"🔄 Falling back to {available_providers[0]}")
                self.provider = available_providers[0]
                self._initialize_provider()
            else:
                raise RuntimeError("No working embedding providers available")
    
    def _initialize_openai(self):
        """Initialize OpenAI embeddings."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # Select best OpenAI model
        if not self.model_name:
            self.model_name = "text-embedding-3-large"  # Best quality as suggested
        
        logger.info(f"✅ OpenAI embeddings initialized with {self.model_name}")
    
    def _initialize_cohere(self):
        """Initialize Cohere embeddings."""
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            raise ValueError("COHERE_API_KEY not found in environment")
        
        self.client = cohere.Client(api_key)
        
        # Select best Cohere model
        if not self.model_name:
            self.model_name = "embed-english-v3.0"  # As suggested
        
        logger.info(f"✅ Cohere embeddings initialized with {self.model_name}")
    
    def _initialize_sentence_transformers(self):
        """Initialize SentenceTransformers (offline)."""
        # Select best offline model
        if not self.model_name:
            # Priority: InstructorXL > bge-large-en-v1.5 > all-MiniLM-L6-v2
            available_models = [
                "hkunlp/instructor-xl",
                "BAAI/bge-large-en-v1.5", 
                "all-MiniLM-L6-v2"
            ]
            
            for model in available_models:
                try:
                    self.model = SentenceTransformer(model)
                    self.model_name = model
                    break
                except Exception as e:
                    logger.warning(f"Failed to load {model}: {e}")
                    continue
            
            if not self.model:
                raise RuntimeError("No SentenceTransformer models could be loaded")
        else:
            self.model = SentenceTransformer(self.model_name)
        
        logger.info(f"✅ SentenceTransformers initialized with {self.model_name}")
    
    def _initialize_ollama(self):
        """Initialize Ollama embeddings."""
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        # Test Ollama connectivity
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama not available at {ollama_url}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}")
        
        self.client = ollama_url
        
        # Select best Ollama embedding model
        if not self.model_name:
            # Try models in order of preference
            available_models = ["nomic-embed-text", "all-minilm", "mxbai-embed-large"]
            
            for model in available_models:
                try:
                    # Test if model is available
                    test_response = requests.post(
                        f"{ollama_url}/api/embeddings",
                        json={"model": model, "prompt": "test"},
                        timeout=10
                    )
                    if test_response.status_code == 200:
                        self.model_name = model
                        break
                except Exception:
                    continue
            
            if not self.model_name:
                self.model_name = "nomic-embed-text"  # Default fallback
        
        logger.info(f"✅ Ollama embeddings initialized with {self.model_name}")
    
    @lru_cache(maxsize=10000)
    def get_embedding_cached(self, text: str) -> List[float]:
        """
        Get embedding with caching (for single texts).
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.get_embedding(text)
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Check cache first
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        
        try:
            if self.provider == 'openai':
                embedding = self._get_openai_embedding(text)
            elif self.provider == 'cohere':
                embedding = self._get_cohere_embedding(text)
            elif self.provider == 'sentence_transformers':
                embedding = self._get_sentence_transformer_embedding(text)
            elif self.provider == 'ollama':
                embedding = self._get_ollama_embedding(text)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Cache the result
            if len(self.embedding_cache) < self.cache_size:
                self.embedding_cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Embedding failed for provider {self.provider}: {e}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Check cache for all texts first
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_hash])
            else:
                embeddings.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Get embeddings for uncached texts
        if uncached_texts:
            try:
                if self.provider == 'openai':
                    new_embeddings = self._get_openai_embeddings_batch(uncached_texts)
                elif self.provider == 'cohere':
                    new_embeddings = self._get_cohere_embeddings_batch(uncached_texts)
                elif self.provider == 'sentence_transformers':
                    new_embeddings = self._get_sentence_transformer_embeddings_batch(uncached_texts)
                elif self.provider == 'ollama':
                    new_embeddings = self._get_ollama_embeddings_batch(uncached_texts)
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")
                
                # Fill in the embeddings and update cache
                for i, embedding in enumerate(new_embeddings):
                    idx = uncached_indices[i]
                    embeddings[idx] = embedding
                    
                    # Cache the result
                    if len(self.embedding_cache) < self.cache_size:
                        text_hash = hashlib.md5(uncached_texts[i].encode()).hexdigest()
                        self.embedding_cache[text_hash] = embedding
                        
            except Exception as e:
                logger.error(f"❌ Batch embedding failed for provider {self.provider}: {e}")
                # Fallback to individual embeddings
                for i, text in enumerate(uncached_texts):
                    try:
                        idx = uncached_indices[i]
                        embeddings[idx] = self.get_embedding(text)
                    except Exception as e2:
                        logger.error(f"❌ Individual embedding also failed: {e2}")
                        # Use zero vector as fallback
                        embeddings[idx] = [0.0] * 1536  # Common embedding dimension
        
        return embeddings
    
    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API."""
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    def _get_openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get batch embeddings from OpenAI API."""
        # OpenAI supports batch processing
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def _get_cohere_embedding(self, text: str) -> List[float]:
        """Get embedding from Cohere API."""
        response = self.client.embed(
            model=self.model_name,
            texts=[text],
            input_type="search_document"
        )
        return response.embeddings[0]
    
    def _get_cohere_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get batch embeddings from Cohere API."""
        response = self.client.embed(
            model=self.model_name,
            texts=texts,
            input_type="search_document"
        )
        return response.embeddings
    
    def _get_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Get embedding from SentenceTransformers."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def _get_sentence_transformer_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get batch embeddings from SentenceTransformers."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def _get_ollama_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama API."""
        response = requests.post(
            f"{self.client}/api/embeddings",
            json={"model": self.model_name, "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embedding"]
    
    def _get_ollama_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get batch embeddings from Ollama API."""
        # Ollama doesn't support batch, so we'll do them individually
        embeddings = []
        for text in texts:
            embedding = self._get_ollama_embedding(text)
            embeddings.append(embedding)
            time.sleep(0.1)  # Small delay to avoid overwhelming the API
        return embeddings
    
    def enhance_text_for_embedding(self, 
                                  text: str, 
                                  metadata: Dict[str, Any]) -> str:
        """
        Enhance text with metadata prefix for better domain-specific embeddings.
        
        Args:
            text: Original text content
            metadata: Metadata dict with product, section, etc.
            
        Returns:
            Enhanced text with context prefix
        """
        # Create context prefix
        prefix_parts = []
        
        if metadata.get('product'):
            prefix_parts.append(f"[product:{metadata['product']}]")
        
        if metadata.get('version'):
            prefix_parts.append(f"[version:{metadata['version']}]")
        
        if metadata.get('section_title'):
            prefix_parts.append(f"[section:{metadata['section_title']}]")
        
        if metadata.get('structural_type'):
            prefix_parts.append(f"[type:{metadata['structural_type']}]")
        
        # Add rule tags if available
        if metadata.get('rule_tags'):
            tags = ",".join(metadata['rule_tags'][:3])  # Limit to 3 tags
            prefix_parts.append(f"[tags:{tags}]")
        
        prefix = " ".join(prefix_parts)
        
        # Combine prefix with text
        if prefix:
            enhanced_text = f"{prefix} {text}"
        else:
            enhanced_text = text
        
        return enhanced_text
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about embedding usage.
        
        Returns:
            Dictionary with embedding statistics
        """
        return {
            'provider': self.provider,
            'model_name': self.model_name,
            'cache_size': len(self.embedding_cache),
            'cache_max': self.cache_size,
            'cache_hit_rate': len(self.embedding_cache) / max(1, self.cache_size)
        }


# Global instance for easy access
_global_embedding_manager = None

def get_embedding_manager(provider: str = "auto", 
                         model_name: Optional[str] = None) -> AdvancedEmbeddingManager:
    """
    Get global embedding manager instance.
    
    Args:
        provider: Embedding provider
        model_name: Specific model name
        
    Returns:
        Global embedding manager instance
    """
    global _global_embedding_manager
    
    if _global_embedding_manager is None:
        _global_embedding_manager = AdvancedEmbeddingManager(
            provider=provider,
            model_name=model_name
        )
    
    return _global_embedding_manager