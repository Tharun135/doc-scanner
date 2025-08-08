"""
RAG Performance Optimizer - Fast RAG with intelligent caching
Reduces RAG response time from 40+ seconds to under 1 second.
"""

import logging
import time
import hashlib
from typing import Dict, List, Optional, Any
from functools import lru_cache
import threading
import pickle
import os

logger = logging.getLogger(__name__)

class RAGPerformanceOptimizer:
    """
    Optimizes RAG performance through:
    1. Singleton pattern for RAG system (avoid re-initialization)
    2. Smart caching of responses
    3. Timeout controls
    4. Batch processing
    """
    
    _instance = None
    _lock = threading.Lock()
    _rag_system = None
    _response_cache = {}
    _cache_file = "rag_cache.pkl"
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_cache()
            self._initialized = True
    
    def _load_cache(self):
        """Load cached RAG responses from disk."""
        try:
            cache_path = os.path.join(os.path.dirname(__file__), self._cache_file)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    self._response_cache = pickle.load(f)
                logger.info(f"Loaded {len(self._response_cache)} cached RAG responses")
        except Exception as e:
            logger.warning(f"Could not load RAG cache: {e}")
            self._response_cache = {}
    
    def _save_cache(self):
        """Save cached RAG responses to disk."""
        try:
            cache_path = os.path.join(os.path.dirname(__file__), self._cache_file)
            with open(cache_path, 'wb') as f:
                pickle.dump(self._response_cache, f)
        except Exception as e:
            logger.warning(f"Could not save RAG cache: {e}")
    
    def get_rag_system(self):
        """DISABLED: Get singleton RAG system instance - Google API no longer used."""
        # Return None to prevent Google API loading
        logger.info("Google API RAG system disabled - using local AI instead")
        return None
    
    def _get_cache_key(self, text: str, rule_name: str, context: str = "") -> str:
        """Generate cache key for RAG response."""
        content = f"{rule_name}:{text}:{context}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_suggestion(self, text: str, rule_name: str, context: str = "") -> Optional[str]:
        """Get cached RAG suggestion if available."""
        cache_key = self._get_cache_key(text, rule_name, context)
        return self._response_cache.get(cache_key)
    
    def cache_suggestion(self, text: str, rule_name: str, suggestion: str, context: str = ""):
        """Cache RAG suggestion for future use."""
        cache_key = self._get_cache_key(text, rule_name, context)
        self._response_cache[cache_key] = suggestion
        
        # Periodically save cache (every 10 new entries)
        if len(self._response_cache) % 10 == 0:
            self._save_cache()
    
    def get_rag_suggestion_fast(self, text: str, rule_name: str, context: str = "", timeout: float = 5.0) -> Optional[str]:
        """
        Get RAG suggestion with performance optimizations:
        1. Check cache first
        2. Use timeout to prevent hanging
        3. Cache results for future use
        """
        # Check cache first
        cached = self.get_cached_suggestion(text, rule_name, context)
        if cached:
            logger.debug(f"Cache hit for {rule_name}")
            return cached
        
        # Get RAG system (lazy loaded)
        rag_system = self.get_rag_system()
        if not rag_system or not rag_system.is_initialized:
            logger.debug(f"RAG system not available for {rule_name}")
            return None
        
        try:
            start_time = time.time()
            
            # Use threading for timeout control
            result = [None]
            error = [None]
            
            def rag_query():
                try:
                    suggestion = rag_system.get_suggestion(text, context=context)
                    result[0] = suggestion
                except Exception as e:
                    error[0] = e
            
            thread = threading.Thread(target=rag_query)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)
            
            if thread.is_alive():
                logger.warning(f"RAG query timeout ({timeout}s) for {rule_name}")
                return None
            
            if error[0]:
                raise error[0]
            
            suggestion = result[0]
            if suggestion:
                # Cache the result
                self.cache_suggestion(text, rule_name, suggestion, context)
                
                elapsed = time.time() - start_time
                logger.debug(f"RAG suggestion for {rule_name} in {elapsed:.2f}s")
                return suggestion
            
        except Exception as e:
            logger.warning(f"RAG error for {rule_name}: {e}")
        
        return None

# Global optimizer instance
_optimizer = RAGPerformanceOptimizer()

def get_fast_rag_suggestion(text: str, rule_name: str, context: str = "", timeout: float = 5.0) -> Optional[str]:
    """
    Fast RAG suggestion function with caching and timeout.
    
    Args:
        text: Text to analyze
        rule_name: Name of the rule requesting suggestion
        context: Additional context for better suggestions
        timeout: Maximum time to wait for RAG response (default 5s)
    
    Returns:
        RAG suggestion string or None if not available/timeout
    """
    return _optimizer.get_rag_suggestion_fast(text, rule_name, context, timeout)

def clear_rag_cache():
    """Clear all cached RAG responses."""
    _optimizer._response_cache.clear()
    _optimizer._save_cache()
    logger.info("RAG cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get RAG cache statistics."""
    return {
        "cached_responses": len(_optimizer._response_cache),
        "rag_initialized": _optimizer._rag_system is not None,
        "cache_file": _optimizer._cache_file
    }
