#!/usr/bin/env python3
"""
RAG Dashboard Performance Optimizer
Implements caching and lazy loading to improve dashboard loading times.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RAGPerformanceCache:
    """Caches RAG system components and statistics to improve performance."""
    
    def __init__(self, cache_duration_minutes: int = 5):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache = {}
        self.lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < self.cache_duration:
                    return value
                else:
                    # Cache expired, remove it
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with current timestamp."""
        with self.lock:
            self.cache[key] = (value, datetime.now())
    
    def clear(self, key: Optional[str] = None) -> None:
        """Clear specific key or entire cache."""
        with self.lock:
            if key:
                self.cache.pop(key, None)
            else:
                self.cache.clear()

# Global cache instance
rag_cache = RAGPerformanceCache()

def cached_result(cache_key_func=None, cache_duration_minutes=5):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_value = rag_cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}, executing function")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            rag_cache.set(cache_key, result)
            logger.debug(f"Cached result for {cache_key} (execution time: {execution_time:.2f}s)")
            return result
        return wrapper
    return decorator

class LazyRAGInitializer:
    """Manages lazy initialization of RAG components."""
    
    def __init__(self):
        self._retriever = None
        self._evaluator = None
        self._initialization_lock = threading.Lock()
        self._initialized = False
    
    def get_retriever(self):
        """Get retriever instance with lazy initialization."""
        if self._retriever is None:
            with self._initialization_lock:
                if self._retriever is None:  # Double-check locking
                    try:
                        from app.advanced_retrieval import AdvancedRetriever
                        logger.info("🔄 Lazy initializing AdvancedRetriever...")
                        start_time = time.time()
                        self._retriever = AdvancedRetriever()
                        init_time = time.time() - start_time
                        logger.info(f"✅ AdvancedRetriever initialized in {init_time:.2f}s")
                    except Exception as e:
                        logger.error(f"Failed to initialize AdvancedRetriever: {e}")
                        return None
        return self._retriever
    
    def get_evaluator(self):
        """Get evaluator instance with lazy initialization."""
        if self._evaluator is None:
            with self._initialization_lock:
                if self._evaluator is None:  # Double-check locking
                    try:
                        from app.rag_evaluation import get_rag_evaluator
                        logger.info("🔄 Lazy initializing RAGEvaluator...")
                        start_time = time.time()
                        self._evaluator = get_rag_evaluator()
                        init_time = time.time() - start_time
                        logger.info(f"✅ RAGEvaluator initialized in {init_time:.2f}s")
                    except Exception as e:
                        logger.error(f"Failed to initialize RAGEvaluator: {e}")
                        return None
        return self._evaluator
    
    def is_initialized(self) -> bool:
        """Check if components are initialized."""
        return self._retriever is not None or self._evaluator is not None

# Global lazy initializer
lazy_rag = LazyRAGInitializer()

@cached_result(cache_duration_minutes=5)
def get_fast_rag_stats() -> Dict[str, Any]:
    """Get RAG statistics with caching for fast dashboard loading."""
    logger.info("🚀 Getting fast RAG stats...")
    start_time = time.time()
    
    # Default stats structure
    stats = {
        'total_chunks': 0,
        'total_queries': 0,
        'avg_relevance': 0.0,
        'success_rate': 0.0,
        'queries_today': 0,
        'documents_count': 0,
        'search_methods': 1,
        'embedding_model': 'N/A',
        'hybrid_available': False,
        'chromadb_available': False,
        'embeddings_available': False,
        'retrieval_accuracy': 0.0,
        'response_relevance': 0.0,
        'context_precision': 0.0,
        'user_satisfaction': 0.0,
        'avg_search_time': 750
    }
    
    try:
        # Check if retriever is available (use global instance first)
        retriever = None
        try:
            # Try to use the global retriever from rag_routes
            from app.rag_routes import retriever as global_retriever, init_rag_system, check_rag_dependencies, init_rag_modules
            
            # If global retriever is None, try to initialize it
            if global_retriever is None:
                # Check if we can initialize the RAG system
                if check_rag_dependencies() and init_rag_modules():
                    logger.info("🔄 Initializing RAG system for stats...")
                    init_rag_system()
                    # Import again to get the updated global retriever
                    from app.rag_routes import retriever as updated_retriever
                    retriever = updated_retriever
                else:
                    logger.warning("⚠️ RAG dependencies not available for stats")
            else:
                retriever = global_retriever
                
            # Fall back to lazy initialization if global retriever still not available
            if retriever is None and lazy_rag._retriever is not None:
                retriever = lazy_rag.get_retriever()
                
        except ImportError as e:
            logger.warning(f"Could not import RAG system: {e}")
            # Fall back to lazy initialization
            if lazy_rag._retriever is not None:
                retriever = lazy_rag.get_retriever()
        
        if retriever:
            retriever_stats = retriever.get_collection_stats()
            stats.update(retriever_stats)
            
            # Update computed stats
            stats.update({
                    'hybrid_available': retriever_stats.get('embeddings_available', False) and retriever_stats.get('tfidf_available', False),
                    'search_methods': 3 if (retriever_stats.get('embeddings_available', False) and retriever_stats.get('tfidf_available', False)) else 1,
                    'embedding_model': 'sentence-transformers' if retriever_stats.get('embeddings_available', False) else 'N/A',
                })
        
        # Check if evaluator is available (don't initialize if not needed)
        if lazy_rag._evaluator is not None:
            evaluator = lazy_rag.get_evaluator()
            if evaluator:
                eval_stats = evaluator.get_performance_stats(days=7)  # Shorter period for faster queries
                stats.update({
                    'total_queries': eval_stats.total_queries,
                    'avg_relevance': eval_stats.avg_relevance_score,
                    'success_rate': eval_stats.success_rate
                })
    
    except Exception as e:
        logger.warning(f"Error getting RAG stats: {e}")
    
    execution_time = time.time() - start_time
    logger.info(f"✅ Fast RAG stats completed in {execution_time:.2f}s")
    return stats

@cached_result(cache_duration_minutes=10)
def get_lightweight_rag_status() -> Dict[str, Any]:
    """Get lightweight RAG system status without heavy initialization."""
    status = {
        'rag_available': False,
        'dependencies_available': False,
        'components_initialized': False,
        'chromadb_available': False,
        'embeddings_available': False
    }
    
    try:
        # Check dependencies without importing heavy modules
        import importlib.util
        
        # Check ChromaDB
        chromadb_spec = importlib.util.find_spec("chromadb")
        status['chromadb_available'] = chromadb_spec is not None
        
        # Check sentence transformers
        st_spec = importlib.util.find_spec("sentence_transformers")
        status['embeddings_available'] = st_spec is not None
        
        status['dependencies_available'] = status['chromadb_available'] and status['embeddings_available']
        status['components_initialized'] = lazy_rag.is_initialized()
        status['rag_available'] = status['dependencies_available']
        
    except Exception as e:
        logger.warning(f"Error checking RAG status: {e}")
    
    return status

def initialize_rag_background():
    """Initialize RAG components in background thread."""
    def init_worker():
        logger.info("🔄 Background RAG initialization started...")
        try:
            lazy_rag.get_retriever()
            lazy_rag.get_evaluator()
            logger.info("✅ Background RAG initialization completed")
        except Exception as e:
            logger.error(f"Background RAG initialization failed: {e}")
    
    thread = threading.Thread(target=init_worker, daemon=True)
    thread.start()
    return thread

def preload_rag_dashboard_data():
    """Preload dashboard data in background to warm up cache."""
    def preload_worker():
        try:
            logger.info("🔄 Preloading RAG dashboard data...")
            get_fast_rag_stats()
            get_lightweight_rag_status()
            logger.info("✅ RAG dashboard data preloaded successfully")
        except Exception as e:
            logger.error(f"Dashboard data preload failed: {e}")
    
    thread = threading.Thread(target=preload_worker, daemon=True)
    thread.start()
    return thread

def clear_rag_cache():
    """Clear all RAG-related caches."""
    rag_cache.clear()
    logger.info("🧹 RAG cache cleared")

if __name__ == "__main__":
    # Test the optimization
    print("🧪 Testing RAG Performance Optimizer")
    print("=" * 50)
    
    # Test 1: Fast status check
    print("\n1. Testing lightweight status check...")
    start = time.time()
    status = get_lightweight_rag_status()
    print(f"   Status check took: {time.time() - start:.2f}s")
    print(f"   RAG available: {status['rag_available']}")
    
    # Test 2: Fast stats (cached)
    print("\n2. Testing fast stats (first call)...")
    start = time.time()
    stats = get_fast_rag_stats()
    print(f"   First stats call took: {time.time() - start:.2f}s")
    
    # Test 3: Fast stats (cached)
    print("\n3. Testing fast stats (cached call)...")
    start = time.time()
    stats = get_fast_rag_stats()
    print(f"   Cached stats call took: {time.time() - start:.2f}s")
    
    print("\n✅ Performance optimizer test completed!")