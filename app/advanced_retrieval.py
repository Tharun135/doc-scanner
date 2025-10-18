"""
Advanced Retrieval System for DocScanner RAG
Implements both keyword-based and embedding-based retrieval with hybrid approaches.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import math
from collections import Counter, defaultdict

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Embedding imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# TF-IDF for keyword search
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Represents a retrieval result with relevance score and metadata."""
    chunk_id: str
    content: str
    relevance_score: float
    retrieval_method: str
    source_doc_id: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None  # For embedding-based retrieval

class AdvancedRetriever:
    """Advanced retrieval system with multiple strategies."""
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "docscanner_knowledge"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.chunk_texts = []
        self.chunk_metadata = []
        
        # Initialize components
        self._init_chromadb()
        self._init_embedding_model()
        self._init_tfidf()
    
    def _init_chromadb(self):
        """Initialize ChromaDB client and collection."""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Vector search will be disabled.")
            return
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(name=self.collection_name)
                logger.info(f"✅ Connected to existing ChromaDB collection: {self.collection_name}")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "DocScanner Knowledge Base"}
                )
                logger.info(f"✅ Created new ChromaDB collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    def _init_embedding_model(self):
        """Initialize sentence transformer model."""
        if not EMBEDDINGS_AVAILABLE:
            logger.warning("Sentence transformers not available. Embedding search will be disabled.")
            return
        
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Loaded embedding model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _init_tfidf(self):
        """Initialize TF-IDF vectorizer."""
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn not available. TF-IDF search will be disabled.")
            return
        
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            logger.info("✅ Initialized TF-IDF vectorizer")
        except Exception as e:
            logger.error(f"Failed to initialize TF-IDF: {e}")
            self.tfidf_vectorizer = None
    
    def index_chunks(self, chunks: List[Any]) -> bool:
        """
        Index chunks in both vector database and TF-IDF index.
        
        Args:
            chunks: List of Chunk objects from chunking_strategies
            
        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return False
        
        success = True
        
        # Prepare data
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for chunk in chunks:
            chunk_ids.append(chunk.id)
            chunk_texts.append(chunk.content)
            
            # Prepare metadata for ChromaDB (must be serializable)
            metadata = {
                'source_doc_id': chunk.source_doc_id,
                'chunk_type': chunk.chunk_type,
                'word_count': chunk.word_count,
                'start_char': chunk.start_char,
                'end_char': chunk.end_char
            }
            
            # Add safe metadata (ChromaDB doesn't support nested dicts)
            if hasattr(chunk, 'metadata') and chunk.metadata:
                for key, value in chunk.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[f'meta_{key}'] = value
                    elif isinstance(value, list) and all(isinstance(x, str) for x in value):
                        metadata[f'meta_{key}'] = ','.join(value)
            
            chunk_metadatas.append(metadata)
        
        # Index in ChromaDB
        if self.collection is not None:
            try:
                # Check for existing IDs to avoid duplicates
                existing_results = self.collection.get(ids=chunk_ids)
                existing_ids = set(existing_results['ids']) if existing_results['ids'] else set()
                
                # Filter out existing chunks
                new_chunk_ids = []
                new_chunk_texts = []
                new_chunk_metadatas = []
                
                for i, chunk_id in enumerate(chunk_ids):
                    if chunk_id not in existing_ids:
                        new_chunk_ids.append(chunk_id)
                        new_chunk_texts.append(chunk_texts[i])
                        new_chunk_metadatas.append(chunk_metadatas[i])
                
                # Add only new chunks
                if new_chunk_ids:
                    self.collection.add(
                        ids=new_chunk_ids,
                        documents=new_chunk_texts,
                        metadatas=new_chunk_metadatas
                    )
                    logger.info(f"✅ Added {len(new_chunk_ids)} new chunks to ChromaDB (skipped {len(chunk_ids) - len(new_chunk_ids)} duplicates, total: {self.collection.count()})")
                else:
                    logger.info(f"⚠️ All {len(chunk_ids)} chunks already exist in ChromaDB")
            except Exception as e:
                logger.error(f"Failed to index chunks in ChromaDB: {e}")
                success = False
        
        # Index in TF-IDF
        if self.tfidf_vectorizer is not None:
            try:
                # Append new chunks to existing data
                if hasattr(self, 'chunk_texts') and self.chunk_texts:
                    all_texts = self.chunk_texts + chunk_texts
                    all_metadata = self.chunk_metadata + chunk_metadatas
                else:
                    all_texts = chunk_texts
                    all_metadata = chunk_metadatas
                
                # Rebuild TF-IDF with all documents
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
                self.chunk_texts = all_texts
                self.chunk_metadata = all_metadata
                
                logger.info(f"✅ Added {len(chunks)} chunks to TF-IDF index (total: {len(all_texts)})")
            except Exception as e:
                logger.error(f"Failed to index chunks in TF-IDF: {e}")
                success = False
        
        return success
    
    def retrieve_embedding(self, query: str, n_results: int = 5, 
                          source_filter: Optional[str] = None) -> List[RetrievalResult]:
        """
        Retrieve using embedding-based similarity search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            source_filter: Optional filter by source type
            
        Returns:
            List of RetrievalResult objects
        """
        if self.collection is None:
            logger.warning("ChromaDB not available for embedding retrieval")
            return []
        
        try:
            # Prepare where clause for filtering
            where_clause = None
            if source_filter:
                where_clause = {"source_type": source_filter}
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Convert to RetrievalResult objects
            retrieval_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to relevance score (0-1, higher is better)
                    relevance_score = max(0, 1 - distance)
                    
                    result = RetrievalResult(
                        chunk_id=results['ids'][0][i],
                        content=doc,
                        relevance_score=relevance_score,
                        retrieval_method="embedding",
                        source_doc_id=metadata.get('source_doc_id', 'unknown'),
                        metadata=metadata,
                        distance=distance
                    )
                    retrieval_results.append(result)
            
            logger.info(f"🔍 Embedding retrieval returned {len(retrieval_results)} results")
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in embedding retrieval: {e}")
            return []
    
    def retrieve_keyword(self, query: str, n_results: int = 5, 
                        source_filter: Optional[str] = None) -> List[RetrievalResult]:
        """
        Retrieve using TF-IDF keyword-based search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            source_filter: Optional filter by source type
            
        Returns:
            List of RetrievalResult objects
        """
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            logger.warning("TF-IDF not available for keyword retrieval")
            return []
        
        try:
            # Vectorize query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = np.argsort(similarity_scores)[::-1][:n_results * 2]  # Get more for filtering
            
            retrieval_results = []
            
            for idx in top_indices:
                if len(retrieval_results) >= n_results:
                    break
                
                metadata = self.chunk_metadata[idx]
                
                # Apply source filter if specified
                if source_filter and metadata.get('meta_source_type') != source_filter:
                    continue
                
                result = RetrievalResult(
                    chunk_id=f"tfidf_{idx}",
                    content=self.chunk_texts[idx],
                    relevance_score=float(similarity_scores[idx]),
                    retrieval_method="keyword",
                    source_doc_id=metadata.get('source_doc_id', 'unknown'),
                    metadata=metadata,
                    distance=None
                )
                retrieval_results.append(result)
            
            logger.info(f"🔍 Keyword retrieval returned {len(retrieval_results)} results")
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error in keyword retrieval: {e}")
            return []
    
    def retrieve_hybrid(self, query: str, n_results: int = 5, 
                       embedding_weight: float = 0.7, keyword_weight: float = 0.3,
                       source_filter: Optional[str] = None) -> List[RetrievalResult]:
        """
        Retrieve using hybrid approach combining embedding and keyword search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            embedding_weight: Weight for embedding scores (0-1)
            keyword_weight: Weight for keyword scores (0-1)
            source_filter: Optional filter by source type
            
        Returns:
            List of RetrievalResult objects sorted by hybrid score
        """
        # Normalize weights
        total_weight = embedding_weight + keyword_weight
        embedding_weight /= total_weight
        keyword_weight /= total_weight
        
        # Get results from both methods
        embedding_results = self.retrieve_embedding(query, n_results * 2, source_filter)
        keyword_results = self.retrieve_keyword(query, n_results * 2, source_filter)
        
        # Combine results
        combined_scores = defaultdict(lambda: {'embedding': 0, 'keyword': 0, 'result': None})
        
        # Add embedding scores
        for result in embedding_results:
            combined_scores[result.content]['embedding'] = result.relevance_score
            combined_scores[result.content]['result'] = result
        
        # Add keyword scores
        for result in keyword_results:
            combined_scores[result.content]['keyword'] = result.relevance_score
            if combined_scores[result.content]['result'] is None:
                combined_scores[result.content]['result'] = result
        
        # Calculate hybrid scores
        hybrid_results = []
        for content, scores in combined_scores.items():
            hybrid_score = (
                embedding_weight * scores['embedding'] +
                keyword_weight * scores['keyword']
            )
            
            result = scores['result']
            result.relevance_score = hybrid_score
            result.retrieval_method = "hybrid"
            result.metadata['embedding_score'] = scores['embedding']
            result.metadata['keyword_score'] = scores['keyword']
            
            hybrid_results.append(result)
        
        # Sort by hybrid score and return top results
        hybrid_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"🔍 Hybrid retrieval returned {len(hybrid_results[:n_results])} results")
        return hybrid_results[:n_results]
    
    def retrieve_contextual(self, query: str, document_context: str = "", 
                          n_results: int = 5) -> List[RetrievalResult]:
        """
        Retrieve with additional document context for better relevance.
        
        Args:
            query: Search query
            document_context: Current document being analyzed for context
            n_results: Number of results to return
            
        Returns:
            List of RetrievalResult objects
        """
        # Enhance query with context
        enhanced_query = query
        if document_context:
            # Extract key terms from document context
            context_words = re.findall(r'\b\w{4,}\b', document_context.lower())
            context_words = [word for word in context_words if word not in {'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were'}]
            
            # Add top context words to query
            if context_words:
                word_counts = Counter(context_words)
                top_context_words = [word for word, _ in word_counts.most_common(3)]
                enhanced_query = f"{query} {' '.join(top_context_words)}"
        
        # Use hybrid retrieval with enhanced query
        results = self.retrieve_hybrid(enhanced_query, n_results)
        
        # Update metadata to indicate contextual retrieval
        for result in results:
            result.retrieval_method = "contextual"
            result.metadata['original_query'] = query
            result.metadata['enhanced_query'] = enhanced_query
            result.metadata['used_context'] = bool(document_context)
        
        return results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed collection."""
        stats = {
            'chromadb_available': CHROMADB_AVAILABLE,
            'embeddings_available': EMBEDDINGS_AVAILABLE,
            'tfidf_available': SKLEARN_AVAILABLE,
            'collection_count': 0,
            'total_chunks': 0
        }
        
        if self.collection is not None:
            try:
                stats['collection_count'] = self.collection.count()
                stats['total_chunks'] = stats['collection_count']
            except:
                pass
        
        if self.tfidf_matrix is not None:
            stats['tfidf_chunks'] = self.tfidf_matrix.shape[0]
            stats['tfidf_features'] = self.tfidf_matrix.shape[1]
        
        return stats
    
    def search_by_source_type(self, query: str, source_type: str, 
                             n_results: int = 5) -> List[RetrievalResult]:
        """Search within a specific source type (manual, style_guide, etc.)."""
        return self.retrieve_hybrid(query, n_results, source_filter=source_type)

# Convenience functions
def create_retriever(db_path: str = "./chroma_db") -> AdvancedRetriever:
    """Create and return a configured retriever."""
    return AdvancedRetriever(db_path=db_path)

def retrieve_for_writing_feedback(query: str, retriever: AdvancedRetriever, 
                                 document_context: str = "") -> List[RetrievalResult]:
    """
    Specialized retrieval function for writing feedback.
    Prioritizes style guides and writing rules.
    """
    # First, try to get style-specific results
    style_results = retriever.search_by_source_type(query, "style_guide", n_results=3)
    
    # Then get general results
    general_results = retriever.retrieve_contextual(query, document_context, n_results=5)
    
    # Combine and deduplicate
    seen_content = set()
    combined_results = []
    
    # Prioritize style guide results
    for result in style_results:
        if result.content not in seen_content:
            result.metadata['prioritized'] = 'style_guide'
            combined_results.append(result)
            seen_content.add(result.content)
    
    # Add general results
    for result in general_results:
        if result.content not in seen_content and len(combined_results) < 5:
            combined_results.append(result)
            seen_content.add(result.content)
    
    return combined_results
