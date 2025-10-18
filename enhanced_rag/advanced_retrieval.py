# enhanced_rag/advanced_retrieval.py
"""
Advanced retrieval system implementing hybrid search with context re-ranking.
Combines semantic search with BM25 and adds cross-encoder re-ranking for precision.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from functools import lru_cache
import chromadb

# Import ranking libraries
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.warning("rank_bm25 not available. Install with: pip install rank-bm25")

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    logging.warning("sentence_transformers not available. Install with: pip install sentence-transformers")

logger = logging.getLogger(__name__)


@dataclass
class AdvancedRetrievalResult:
    """Enhanced retrieval result with comprehensive scoring."""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    semantic_score: float
    bm25_score: float
    rerank_score: float
    hybrid_score: float
    source: str  # 'semantic', 'bm25', 'both'
    confidence: float
    relevance_explanation: str


class AdvancedHybridRetriever:
    """
    Advanced hybrid retrieval system with context re-ranking.
    Implements the complete retrieval pipeline with quality optimizations.
    """
    
    def __init__(self,
                 chroma_collection: chromadb.Collection,
                 semantic_weight: float = 0.6,
                 bm25_weight: float = 0.4,
                 rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 max_initial_results: int = 20,
                 max_final_results: int = 5,
                 enable_reranking: bool = True):
        """
        Initialize advanced hybrid retriever.
        
        Args:
            chroma_collection: ChromaDB collection for semantic search
            semantic_weight: Weight for semantic search scores
            bm25_weight: Weight for BM25 scores  
            rerank_model: Cross-encoder model for re-ranking
            max_initial_results: Maximum results from initial retrieval
            max_final_results: Maximum results after re-ranking
            enable_reranking: Whether to use cross-encoder re-ranking
        """
        self.collection = chroma_collection
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.max_initial_results = max_initial_results
        self.max_final_results = max_final_results
        self.enable_reranking = enable_reranking
        
        # Initialize BM25 index
        self.bm25_index = None
        self.corpus_texts = []
        self.corpus_ids = []
        self.corpus_metadata = []
        
        # Initialize cross-encoder for re-ranking
        self.cross_encoder = None
        if enable_reranking and CROSS_ENCODER_AVAILABLE:
            try:
                self.cross_encoder = CrossEncoder(rerank_model)
                logger.info(f"✅ Cross-encoder initialized: {rerank_model}")
            except Exception as e:
                logger.warning(f"Failed to load cross-encoder {rerank_model}: {e}")
                self.enable_reranking = False
        
        # Build indexes
        self._build_indexes()
        
        # Performance tracking
        self.retrieval_stats = {
            'total_queries': 0,
            'semantic_queries': 0,
            'bm25_queries': 0,
            'hybrid_queries': 0,
            'rerank_queries': 0,
            'avg_response_time': 0.0
        }
        
        logger.info(f"✅ Advanced hybrid retriever initialized")
    
    def _build_indexes(self):
        """Build BM25 and other indexes from ChromaDB data."""
        if not BM25_AVAILABLE:
            logger.warning("BM25 not available - semantic search only")
            return
        
        try:
            # Get all documents from ChromaDB
            results = self.collection.get()
            
            self.corpus_texts = results.get("documents", [])
            self.corpus_ids = results.get("ids", [])
            self.corpus_metadata = results.get("metadatas", [])
            
            if not self.corpus_texts:
                logger.warning("No documents found for BM25 indexing")
                return
            
            # Tokenize corpus for BM25
            tokenized_corpus = [doc.lower().split() for doc in self.corpus_texts]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            
            logger.info(f"✅ BM25 index built with {len(self.corpus_texts)} documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to build BM25 index: {e}")
    
    def retrieve_advanced(self,
                         query: str,
                         filters: Optional[Dict[str, Any]] = None,
                         use_semantic: bool = True,
                         use_bm25: bool = True,
                         use_reranking: bool = None) -> List[AdvancedRetrievalResult]:
        """
        Advanced retrieval with hybrid search and re-ranking.
        
        Args:
            query: Search query
            filters: Metadata filters for ChromaDB
            use_semantic: Whether to use semantic search
            use_bm25: Whether to use BM25 search
            use_reranking: Whether to use re-ranking (None = auto)
            
        Returns:
            List of advanced retrieval results
        """
        start_time = time.time()
        self.retrieval_stats['total_queries'] += 1
        
        if use_reranking is None:
            use_reranking = self.enable_reranking
        
        try:
            # Step 1: Get initial results from both methods
            semantic_results = []
            bm25_results = []
            
            if use_semantic:
                semantic_results = self._semantic_search(query, filters)
                self.retrieval_stats['semantic_queries'] += 1
            
            if use_bm25 and self.bm25_index:
                bm25_results = self._bm25_search(query, filters)
                self.retrieval_stats['bm25_queries'] += 1
            
            # Step 2: Combine and deduplicate results
            combined_results = self._combine_results(semantic_results, bm25_results)
            
            if combined_results:
                self.retrieval_stats['hybrid_queries'] += 1
            
            # Step 3: Apply re-ranking if enabled
            if use_reranking and self.cross_encoder and combined_results:
                combined_results = self._rerank_results(query, combined_results)
                self.retrieval_stats['rerank_queries'] += 1
            
            # Step 4: Apply dynamic context window
            final_results = self._apply_dynamic_context_window(query, combined_results)
            
            # Update timing stats
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            return final_results[:self.max_final_results]
            
        except Exception as e:
            logger.error(f"❌ Advanced retrieval failed: {e}")
            return []
    
    def _semantic_search(self, 
                        query: str, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform semantic search using ChromaDB."""
        try:
            # Build where clause for filtering
            where_clause = self._build_where_clause(filters) if filters else None
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=self.max_initial_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to standard format
            semantic_results = []
            if results["ids"][0]:  # Check if we got results
                for i in range(len(results["ids"][0])):
                    result = {
                        'chunk_id': results["ids"][0][i],
                        'text': results["documents"][0][i],
                        'metadata': results["metadatas"][0][i] or {},
                        'distance': results["distances"][0][i],
                        'semantic_score': 1.0 - results["distances"][0][i],  # Convert distance to score
                        'source': 'semantic'
                    }
                    semantic_results.append(result)
            
            return semantic_results
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    def _bm25_search(self, 
                    query: str, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform BM25 search using local index."""
        if not self.bm25_index:
            return []
        
        try:
            # Tokenize query
            tokenized_query = query.lower().split()
            
            # Get BM25 scores
            scores = self.bm25_index.get_scores(tokenized_query)
            
            # Get top results
            top_indices = np.argsort(scores)[::-1][:self.max_initial_results]
            
            bm25_results = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include results with positive scores
                    result = {
                        'chunk_id': self.corpus_ids[idx],
                        'text': self.corpus_texts[idx],
                        'metadata': self.corpus_metadata[idx] or {},
                        'bm25_score': float(scores[idx]),
                        'source': 'bm25'
                    }
                    
                    # Apply filters if specified
                    if not filters or self._matches_filters(result['metadata'], filters):
                        bm25_results.append(result)
            
            return bm25_results
            
        except Exception as e:
            logger.error(f"❌ BM25 search failed: {e}")
            return []
    
    def _combine_results(self, 
                        semantic_results: List[Dict[str, Any]], 
                        bm25_results: List[Dict[str, Any]]) -> List[AdvancedRetrievalResult]:
        """Combine and deduplicate results from different search methods."""
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            chunk_id = result['chunk_id']
            combined[chunk_id] = AdvancedRetrievalResult(
                chunk_id=chunk_id,
                text=result['text'],
                metadata=result['metadata'],
                semantic_score=result.get('semantic_score', 0.0),
                bm25_score=0.0,
                rerank_score=0.0,
                hybrid_score=0.0,
                source='semantic',
                confidence=0.0,
                relevance_explanation=""
            )
        
        # Add or merge BM25 results
        for result in bm25_results:
            chunk_id = result['chunk_id']
            if chunk_id in combined:
                # Update existing result
                combined[chunk_id].bm25_score = result.get('bm25_score', 0.0)
                combined[chunk_id].source = 'both'
            else:
                # Add new result
                combined[chunk_id] = AdvancedRetrievalResult(
                    chunk_id=chunk_id,
                    text=result['text'],
                    metadata=result['metadata'],
                    semantic_score=0.0,
                    bm25_score=result.get('bm25_score', 0.0),
                    rerank_score=0.0,
                    hybrid_score=0.0,
                    source='bm25',
                    confidence=0.0,
                    relevance_explanation=""
                )
        
        # Calculate hybrid scores
        for result in combined.values():
            result.hybrid_score = (
                self.semantic_weight * result.semantic_score + 
                self.bm25_weight * result.bm25_score
            )
        
        # Sort by hybrid score
        return sorted(combined.values(), key=lambda x: x.hybrid_score, reverse=True)
    
    def _rerank_results(self, 
                       query: str, 
                       results: List[AdvancedRetrievalResult]) -> List[AdvancedRetrievalResult]:
        """Re-rank results using cross-encoder for better precision."""
        if not self.cross_encoder or not results:
            return results
        
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = [(query, result.text) for result in results]
            
            # Get re-ranking scores
            rerank_scores = self.cross_encoder.predict(pairs)
            
            # Update results with re-ranking scores
            for i, result in enumerate(results):
                result.rerank_score = float(rerank_scores[i])
                
                # Update hybrid score to include re-ranking
                result.hybrid_score = (
                    0.4 * result.hybrid_score +  # Reduce weight of original score
                    0.6 * result.rerank_score     # Higher weight for re-ranking
                )
                
                # Update confidence based on re-ranking score
                result.confidence = min(1.0, max(0.0, result.rerank_score))
            
            # Re-sort by new hybrid score
            return sorted(results, key=lambda x: x.hybrid_score, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Re-ranking failed: {e}")
            return results
    
    def _apply_dynamic_context_window(self, 
                                    query: str, 
                                    results: List[AdvancedRetrievalResult]) -> List[AdvancedRetrievalResult]:
        """Apply dynamic context window based on query and confidence."""
        if not results:
            return results
        
        # Calculate dynamic window size based on:
        # 1. Query length (longer queries need more context)
        # 2. Top result confidence (higher confidence = fewer results needed)
        # 3. Score distribution (tight distribution = fewer results needed)
        
        query_length = len(query.split())
        top_confidence = results[0].confidence if results else 0.0
        
        # Base window size
        base_window = self.max_final_results
        
        # Adjust based on query length
        if query_length > 20:
            window_size = min(base_window + 2, 8)  # Longer queries need more context
        elif query_length < 5:
            window_size = max(base_window - 1, 2)  # Short queries need less context
        else:
            window_size = base_window
        
        # Adjust based on confidence
        if top_confidence > 0.8:
            window_size = max(window_size - 1, 2)  # High confidence = fewer results
        elif top_confidence < 0.5:
            window_size = min(window_size + 1, 8)  # Low confidence = more results
        
        # Add relevance explanations
        for i, result in enumerate(results[:window_size]):
            if result.source == 'both':
                result.relevance_explanation = f"High relevance (semantic + keyword match)"
            elif result.source == 'semantic':
                result.relevance_explanation = f"Semantic similarity to query"
            else:
                result.relevance_explanation = f"Keyword match"
            
            if result.rerank_score > 0:
                result.relevance_explanation += f" (re-ranked: {result.rerank_score:.2f})"
        
        return results[:window_size]
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from filters."""
        where_clause = {}
        
        for key, value in filters.items():
            if key == 'product' and value:
                where_clause['product'] = value
            elif key == 'version' and value:
                where_clause['version'] = value
            elif key == 'section_title' and value:
                where_clause['section_title'] = {"$contains": value}
            elif key == 'rule_tags' and value:
                if isinstance(value, list):
                    where_clause['rule_tags'] = {"$in": value}
                else:
                    where_clause['rule_tags'] = {"$contains": value}
        
        return where_clause
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the given filters."""
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            metadata_value = metadata[key]
            
            if key == 'rule_tags':
                if isinstance(value, list):
                    if not any(tag in metadata_value for tag in value):
                        return False
                else:
                    if value not in metadata_value:
                        return False
            elif key == 'section_title':
                if value.lower() not in metadata_value.lower():
                    return False
            else:
                if metadata_value != value:
                    return False
        
        return True
    
    def _update_response_time(self, response_time: float):
        """Update average response time statistics."""
        current_avg = self.retrieval_stats['avg_response_time']
        total_queries = self.retrieval_stats['total_queries']
        
        # Calculate running average
        new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
        self.retrieval_stats['avg_response_time'] = new_avg
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval performance statistics."""
        stats = self.retrieval_stats.copy()
        stats['bm25_available'] = self.bm25_index is not None
        stats['reranking_available'] = self.cross_encoder is not None
        stats['semantic_weight'] = self.semantic_weight
        stats['bm25_weight'] = self.bm25_weight
        return stats
    
    def optimize_weights(self, 
                        query_results_pairs: List[Tuple[str, List[str]]],
                        ground_truth_relevance: List[List[float]]):
        """
        Optimize semantic and BM25 weights based on evaluation data.
        
        Args:
            query_results_pairs: List of (query, [relevant_doc_ids]) pairs
            ground_truth_relevance: Relevance scores for each query-doc pair
        """
        # This would implement weight optimization using validation data
        # For now, keeping the current weights
        logger.info("Weight optimization not yet implemented")


def create_advanced_retriever(chroma_collection: chromadb.Collection,
                            semantic_weight: float = 0.6,
                            enable_reranking: bool = True) -> AdvancedHybridRetriever:
    """
    Create an advanced hybrid retriever instance.
    
    Args:
        chroma_collection: ChromaDB collection
        semantic_weight: Weight for semantic search
        enable_reranking: Whether to enable cross-encoder re-ranking
        
    Returns:
        Configured advanced retriever
    """
    return AdvancedHybridRetriever(
        chroma_collection=chroma_collection,
        semantic_weight=semantic_weight,
        bm25_weight=1.0 - semantic_weight,
        enable_reranking=enable_reranking
    )
