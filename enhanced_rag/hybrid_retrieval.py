# enhanced_rag/hybrid_retrieval.py
"""
Hybrid retrieval system combining semantic search (ChromaDB) with BM25 exact-match.
Implements the dual-search approach for better recall on both semantic and exact matches.
"""
import chromadb
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from functools import lru_cache

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    print("Warning: rank_bm25 not installed. Install with: pip install rank-bm25")
    BM25_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Structured result from hybrid retrieval"""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    semantic_score: float
    bm25_score: float
    hybrid_score: float
    source: str  # 'semantic', 'bm25', or 'both'


class HybridRetriever:
    """
    Hybrid retrieval combining ChromaDB semantic search with BM25.
    Provides better coverage for both conceptual and exact-match queries.
    """
    
    def __init__(self, 
                 chroma_collection: chromadb.Collection,
                 alpha: float = 0.6,
                 cache_size: int = 1000):
        """
        Initialize hybrid retriever.
        
        Args:
            chroma_collection: ChromaDB collection for semantic search
            alpha: Weight for semantic score (1-alpha for BM25 score)
            cache_size: Size of LRU cache for repeated queries
        """
        self.collection = chroma_collection
        self.alpha = alpha
        self.bm25_index = None
        self.corpus_texts = []
        self.corpus_ids = []
        self.corpus_metadata = []
        
        # Build BM25 index from ChromaDB data
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """Build BM25 index from all documents in ChromaDB collection"""
        if not BM25_AVAILABLE:
            logger.warning("BM25 not available - using semantic search only")
            return
            
        try:
            # Get all documents from ChromaDB
            try:
                results = self.collection.get()  # Get everything, let ChromaDB handle include automatically
                
                self.corpus_texts = results.get("documents", [])
                self.corpus_ids = results.get("ids", [])
                self.corpus_metadata = results.get("metadatas", [])
                
                # Fallback if we don't get IDs
                if not self.corpus_ids and self.corpus_texts:
                    self.corpus_ids = [f"doc_{i}" for i in range(len(self.corpus_texts))]
                    
            except Exception as e:
                logger.warning(f"Failed to get documents from ChromaDB: {e}")
                # Try alternative approach
                try:
                    results = self.collection.get(limit=1000)  # Get up to 1000 docs
                    self.corpus_texts = results.get("documents", [])
                    self.corpus_ids = results.get("ids", [])
                    self.corpus_metadata = results.get("metadatas", [])
                    
                    if not self.corpus_ids and self.corpus_texts:
                        self.corpus_ids = [f"doc_{i}" for i in range(len(self.corpus_texts))]
                        
                except Exception as e2:
                    logger.error(f"Alternative approach also failed: {e2}")
                    return
            
            if not self.corpus_texts:
                logger.warning("No documents found in ChromaDB for BM25 indexing")
                return
                
            # Tokenize documents for BM25
            tokenized_corpus = [doc.lower().split() for doc in self.corpus_texts]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            
            logger.info(f"Built BM25 index with {len(self.corpus_texts)} documents")
            
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {e}")
            self.bm25_index = None
    
    @lru_cache(maxsize=1000)
    def _cached_semantic_search(self, query: str, n_results: int) -> Tuple:
        """Cached semantic search to avoid repeated ChromaDB calls"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Convert to tuple for caching (lists aren't hashable)
            docs = tuple(results.get("documents", [[]])[0])
            metas = tuple(results.get("metadatas", [[]])[0])
            distances = tuple(results.get("distances", [[]])[0] if results.get("distances") else [])
            ids = tuple(results.get("ids", [[]])[0] if results.get("ids") else range(len(docs)))
            
            return docs, metas, distances, ids
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return (), (), (), ()
    
    def _bm25_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Perform BM25 search and return (index, score) pairs"""
        if not self.bm25_index or not BM25_AVAILABLE:
            return []
        
        try:
            query_tokens = query.lower().split()
            scores = self.bm25_index.get_scores(query_tokens)
            
            # Get top K indices with scores
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [(idx, scores[idx]) for idx in top_indices if scores[idx] > 0]
            
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to 0-1 range using min-max normalization"""
        if not scores or len(scores) == 1:
            return scores
            
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [0.5] * len(scores)  # All scores equal
            
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def hybrid_retrieve(self, 
                       query: str, 
                       top_k: int = 10,
                       semantic_k: int = 15,
                       bm25_k: int = 15) -> List[RetrievalResult]:
        """
        Perform hybrid retrieval combining semantic and BM25 search.
        
        Args:
            query: Search query
            top_k: Final number of results to return
            semantic_k: Number of semantic results to consider
            bm25_k: Number of BM25 results to consider
        
        Returns:
            List of RetrievalResult objects ranked by hybrid score
        """
        results_map = {}  # chunk_id -> RetrievalResult
        
        # 1. Semantic search
        sem_docs, sem_metas, sem_distances, sem_ids = self._cached_semantic_search(
            query, semantic_k
        )
        
        if sem_docs:
            # Convert distances to similarity scores (lower distance = higher similarity)
            sem_similarities = [max(0, 1.0 - dist) for dist in sem_distances]
            sem_similarities = self._normalize_scores(sem_similarities)
            
            for i, (doc, meta, sim, chunk_id) in enumerate(zip(
                sem_docs, sem_metas, sem_similarities, sem_ids
            )):
                results_map[chunk_id] = RetrievalResult(
                    chunk_id=chunk_id,
                    text=doc,
                    metadata=meta,
                    semantic_score=sim,
                    bm25_score=0.0,
                    hybrid_score=0.0,  # Will be calculated later
                    source='semantic'
                )
        
        # 2. BM25 search
        bm25_results = self._bm25_search(query, bm25_k)
        
        if bm25_results:
            bm25_scores = [score for _, score in bm25_results]
            normalized_bm25_scores = self._normalize_scores(bm25_scores)
            
            for (idx, _), norm_score in zip(bm25_results, normalized_bm25_scores):
                if idx < len(self.corpus_ids):
                    chunk_id = self.corpus_ids[idx]
                    text = self.corpus_texts[idx]
                    metadata = self.corpus_metadata[idx] if idx < len(self.corpus_metadata) else {}
                    
                    if chunk_id in results_map:
                        # Update existing result with BM25 score
                        results_map[chunk_id].bm25_score = norm_score
                        results_map[chunk_id].source = 'both'
                    else:
                        # New result from BM25 only
                        results_map[chunk_id] = RetrievalResult(
                            chunk_id=chunk_id,
                            text=text,
                            metadata=metadata,
                            semantic_score=0.0,
                            bm25_score=norm_score,
                            hybrid_score=0.0,
                            source='bm25'
                        )
        
        # 3. Calculate hybrid scores and rank
        final_results = []
        
        for result in results_map.values():
            # Hybrid score: weighted combination
            result.hybrid_score = (
                self.alpha * result.semantic_score + 
                (1 - self.alpha) * result.bm25_score
            )
            final_results.append(result)
        
        # Sort by hybrid score (descending)
        final_results.sort(key=lambda x: x.hybrid_score, reverse=True)
        
        # Return top K
        return final_results[:top_k]
    
    def retrieve_with_filters(self,
                            query: str,
                            top_k: int = 10,
                            product_filter: Optional[str] = None,
                            version_filter: Optional[str] = None,
                            section_filter: Optional[str] = None) -> List[RetrievalResult]:
        """
        Retrieve with metadata filters for better relevance.
        
        Args:
            query: Search query
            top_k: Number of results
            product_filter: Filter by product name
            version_filter: Filter by version
            section_filter: Filter by section title
        
        Returns:
            Filtered and ranked results
        """
        # Get initial results
        results = self.hybrid_retrieve(query, top_k * 2)  # Get more for filtering
        
        # Apply filters
        filtered_results = []
        
        for result in results:
            metadata = result.metadata
            
            # Check filters
            if product_filter and metadata.get('product', '') != product_filter:
                continue
            if version_filter and metadata.get('version', '') != version_filter:
                continue
            if section_filter and section_filter.lower() not in metadata.get('section_title', '').lower():
                continue
                
            filtered_results.append(result)
            
            if len(filtered_results) >= top_k:
                break
        
        return filtered_results
    
    def get_retrieval_stats(self, query: str) -> Dict[str, Any]:
        """Get statistics about retrieval for a query (for debugging/evaluation)"""
        results = self.hybrid_retrieve(query, top_k=10)
        
        semantic_count = sum(1 for r in results if 'semantic' in r.source)
        bm25_count = sum(1 for r in results if 'bm25' in r.source)
        both_count = sum(1 for r in results if r.source == 'both')
        
        avg_semantic = np.mean([r.semantic_score for r in results if r.semantic_score > 0])
        avg_bm25 = np.mean([r.bm25_score for r in results if r.bm25_score > 0])
        avg_hybrid = np.mean([r.hybrid_score for r in results])
        
        return {
            'total_results': len(results),
            'semantic_only': semantic_count - both_count,
            'bm25_only': bm25_count - both_count,
            'both_methods': both_count,
            'avg_semantic_score': float(avg_semantic) if not np.isnan(avg_semantic) else 0.0,
            'avg_bm25_score': float(avg_bm25) if not np.isnan(avg_bm25) else 0.0,
            'avg_hybrid_score': float(avg_hybrid) if not np.isnan(avg_hybrid) else 0.0,
            'query_length': len(query.split()),
            'has_exact_matches': any(query.lower() in r.text.lower() for r in results[:5])
        }


# Quick installation helper
def install_bm25():
    """Helper to install rank-bm25 if needed"""
    if not BM25_AVAILABLE:
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rank-bm25"])
            print("✅ Successfully installed rank-bm25")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install rank-bm25")
            return False
    return True


# Example usage and testing
if __name__ == "__main__":
    print("Testing Hybrid Retrieval System")
    print("=" * 50)
    
    # This would normally use your actual ChromaDB collection
    print("Note: This requires a real ChromaDB collection to test properly")
    print("The HybridRetriever integrates with your existing ChromaDB setup")
    
    if not BM25_AVAILABLE:
        print("\n⚠️  BM25 not available. Installing...")
        install_bm25()
