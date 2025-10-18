# enhanced_rag/enhanced_vectorstore.py
"""
Enhanced vector store manager with improved indexing, metadata handling, and caching.
Integrates the new chunking strategy and hybrid retrieval with your existing ChromaDB setup.
"""
import os
import chromadb
import logging
from typing import List, Dict, Any, Tuple, Optional
from functools import lru_cache
import hashlib
import json
from datetime import datetime

from .chunking import (
    chunk_document_hierarchical,
    prepare_chunk_for_embedding,
    generate_chunk_id,
    create_enhanced_metadata
)
from .hybrid_retrieval import HybridRetriever

logger = logging.getLogger(__name__)

# Config with improved defaults
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "docscanner_enhanced")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Cache for performance
_collection_cache = {}
_hybrid_retriever_cache = {}


class EnhancedVectorStore:
    """
    Enhanced vector store with improved chunking, metadata, and hybrid retrieval.
    Drop-in replacement for the existing vectorstore with better performance.
    """
    
    def __init__(self, 
                 collection_name: str = CHROMA_COLLECTION,
                 chroma_path: str = CHROMA_PATH,
                 embedding_model: str = OLLAMA_EMBED_MODEL):
        """
        Initialize enhanced vector store.
        
        Args:
            collection_name: ChromaDB collection name
            chroma_path: Path to ChromaDB storage
            embedding_model: Ollama embedding model name
        """
        self.collection_name = collection_name
        self.chroma_path = chroma_path
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        self.hybrid_retriever = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(path=self.chroma_path)
            
            # Enhanced embedding function with better config
            embedding_function = chromadb.utils.embedding_functions.OllamaEmbeddingFunction(
                url=OLLAMA_URL,
                model_name=self.embedding_model,
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Enhanced DocScanner RAG with hybrid retrieval",
                    "version": "2.0"
                }
            )
            
            # Initialize hybrid retriever
            self.hybrid_retriever = HybridRetriever(self.collection)
            
            logger.info(f"✅ Enhanced vector store initialized: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced vector store: {e}")
            raise
    
    def ingest_document(self,
                       document_text: str,
                       source_doc_id: str,
                       product: str = "docscanner",
                       version: str = "1.0",
                       additional_metadata: Dict[str, Any] = None) -> int:
        """
        Ingest a document with enhanced chunking and metadata.
        
        Args:
            document_text: Full document text
            source_doc_id: Unique document identifier
            product: Product name
            version: Product version
            additional_metadata: Extra metadata to include
        
        Returns:
            Number of chunks created
        """
        if additional_metadata is None:
            additional_metadata = {}
        
        # Step 1: Create enhanced chunks with metadata
        chunks_with_metadata = chunk_document_hierarchical(
            document_text=document_text,
            source_doc_id=source_doc_id,
            product=product,
            version=version,
            max_sentences_per_chunk=5  # Configurable chunk size
        )
        
        if not chunks_with_metadata:
            logger.warning(f"No chunks created for document: {source_doc_id}")
            return 0
        
        # Step 2: Prepare for ChromaDB insertion
        ids = []
        documents = []
        metadatas = []
        
        for chunk_text, metadata in chunks_with_metadata:
            # Generate unique ID
            chunk_id = generate_chunk_id(chunk_text, metadata)
            
            # Prepare enhanced text for embedding (with metadata prefix)
            enhanced_text = prepare_chunk_for_embedding(chunk_text, metadata)
            
            # Merge additional metadata
            final_metadata = {**metadata, **additional_metadata}
            
            ids.append(chunk_id)
            documents.append(enhanced_text)  # This goes to embedding
            metadatas.append(final_metadata)
        
        # Step 3: Upsert to ChromaDB (handles deduplication)
        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            # Rebuild hybrid retriever index with new data
            self.hybrid_retriever._build_bm25_index()
            
            logger.info(f"✅ Ingested {len(chunks_with_metadata)} chunks from {source_doc_id}")
            return len(chunks_with_metadata)
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest document {source_doc_id}: {e}")
            raise
    
    def query_enhanced(self,
                      query_text: str,
                      n_results: int = 5,
                      use_hybrid: bool = True,
                      product_filter: Optional[str] = None,
                      version_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Enhanced query with hybrid retrieval and filtering.
        
        Args:
            query_text: Search query
            n_results: Number of results to return
            use_hybrid: Whether to use hybrid (semantic + BM25) retrieval
            product_filter: Filter by product
            version_filter: Filter by version
        
        Returns:
            List of retrieval results with scores and metadata
        """
        if use_hybrid and self.hybrid_retriever:
            # Use hybrid retrieval
            results = self.hybrid_retriever.retrieve_with_filters(
                query=query_text,
                top_k=n_results,
                product_filter=product_filter,
                version_filter=version_filter
            )
            
            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.chunk_id,
                    'text': result.text,
                    'metadata': result.metadata,
                    'semantic_score': result.semantic_score,
                    'bm25_score': result.bm25_score,
                    'hybrid_score': result.hybrid_score,
                    'source': result.source
                })
            
            return formatted_results
        
        else:
            # Fall back to pure semantic search
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
                
                formatted_results = []
                ids = results.get('ids', [[]])[0]
                documents = results.get('documents', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0] if results.get('distances') else []
                
                for i in range(len(documents)):
                    result_dict = {
                        'id': ids[i] if i < len(ids) else f'result_{i}',
                        'text': documents[i],
                        'metadata': metadatas[i] if i < len(metadatas) else {},
                        'source': 'semantic_only'
                    }
                    if i < len(distances):
                        result_dict['distance'] = distances[i]
                    formatted_results.append(result_dict)
                
                return formatted_results
                
            except Exception as e:
                logger.error(f"❌ Query failed: {e}")
                return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            # Sample some documents to get metadata stats
            sample = self.collection.get(limit=100)
            
            products = set()
            versions = set()
            sections = set()
            rule_tags = set()
            
            for meta in sample.get('metadatas', []):
                if meta:
                    products.add(meta.get('product', 'unknown'))
                    versions.add(meta.get('version', 'unknown'))
                    sections.add(meta.get('section_title', 'unknown'))
                    if meta.get('rule_tags'):
                        rule_tags.update(meta['rule_tags'].split(','))
            
            return {
                'total_chunks': count,
                'unique_products': len(products),
                'unique_versions': len(versions),
                'unique_sections': len(sections),
                'unique_rule_tags': len(rule_tags),
                'sample_products': list(products)[:5],
                'sample_sections': list(sections)[:10],
                'hybrid_retrieval_available': self.hybrid_retriever is not None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {'error': str(e)}
    
    def test_retrieval(self, test_queries: List[str] = None) -> Dict[str, Any]:
        """Test the retrieval system with sample queries"""
        if test_queries is None:
            test_queries = [
                "passive voice problems",
                "adverb usage rules", 
                "click on button instructions",
                "writing clarity improvement"
            ]
        
        test_results = {}
        
        for query in test_queries:
            try:
                # Test hybrid retrieval
                results = self.query_enhanced(query, n_results=3, use_hybrid=True)
                
                # Get retrieval stats
                stats = self.hybrid_retriever.get_retrieval_stats(query) if self.hybrid_retriever else {}
                
                test_results[query] = {
                    'results_count': len(results),
                    'top_score': results[0]['hybrid_score'] if results else 0,
                    'retrieval_stats': stats,
                    'sample_result': results[0]['text'][:100] + "..." if results else "No results"
                }
                
            except Exception as e:
                test_results[query] = {'error': str(e)}
        
        return test_results
    
    def migrate_from_existing_collection(self, 
                                       old_collection_name: str = "docscanner_solutions") -> bool:
        """
        Migrate data from existing collection to enhanced format.
        
        Args:
            old_collection_name: Name of existing collection to migrate from
        
        Returns:
            True if migration successful
        """
        try:
            # Get existing collection
            old_collection = self.client.get_collection(old_collection_name)
            
            # Get all existing data
            old_data = old_collection.get()
            
            migrated_count = 0
            
            documents = old_data.get('documents', [])
            metadatas = old_data.get('metadatas', [])
            
            for i, (document, metadata) in enumerate(zip(documents, metadatas)):
                if not document:  # Skip empty documents
                    continue
                # Enhance metadata for new schema
                enhanced_metadata = create_enhanced_metadata(
                    chunk_text=document,
                    source_doc_id=metadata.get('source_doc_id', f'migrated_{i}'),
                    product=metadata.get('product', 'docscanner'),
                    version=metadata.get('version', '1.0'),
                    section_title=metadata.get('title', metadata.get('section_title', 'Migrated')),
                    chunk_index=i
                )
                
                # Preserve original metadata
                enhanced_metadata.update(metadata)
                
                # Add to new collection with enhanced text
                enhanced_text = prepare_chunk_for_embedding(document, enhanced_metadata)
                
                self.collection.upsert(
                    ids=[f"migrated_{i}"],
                    documents=[enhanced_text],
                    metadatas=[enhanced_metadata]
                )
                
                migrated_count += 1
            
            # Rebuild hybrid index
            self.hybrid_retriever._build_bm25_index()
            
            logger.info(f"✅ Migrated {migrated_count} documents from {old_collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False


# Factory function for easy integration with existing code
def get_enhanced_store(collection_name: str = None) -> EnhancedVectorStore:
    """Factory function to get enhanced vector store (with caching)"""
    if collection_name is None:
        collection_name = CHROMA_COLLECTION
    
    cache_key = f"{collection_name}_{CHROMA_PATH}"
    
    if cache_key not in _collection_cache:
        _collection_cache[cache_key] = EnhancedVectorStore(collection_name)
    
    return _collection_cache[cache_key]


# Compatibility functions for drop-in replacement
def get_store():
    """Drop-in replacement for existing get_store() function"""
    return get_enhanced_store().collection


def upsert_rules(items: List[Dict[str, Any]]):
    """Drop-in replacement for existing upsert_rules() function"""
    store = get_enhanced_store()
    
    for item in items:
        # Convert old format to new document format
        store.ingest_document(
            document_text=item.get('text', ''),
            source_doc_id=item.get('id', 'unknown'),
            additional_metadata=item.get('metadata', {})
        )


# Example usage and testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Enhanced Vector Store")
    print("=" * 50)
    
    # Initialize enhanced store
    store = get_enhanced_store("test_enhanced")
    
    # Test document ingestion
    sample_doc = """
# Writing Rules for Technical Documentation

## Passive Voice Issues
Passive voice should be avoided in technical writing. Documents are made clearer when active voice is used.

## Adverb Usage
Really good writing doesn't use unnecessary adverbs. Simply remove them for clarity.

## Click Instructions  
Don't say "click on the button." Instead, say "click the button."
    """
    
    count = store.ingest_document(
        document_text=sample_doc,
        source_doc_id="test_writing_rules",
        product="docscanner",
        version="2.0"
    )
    
    print(f"✅ Ingested {count} chunks")
    
    # Test retrieval
    results = store.query_enhanced("passive voice problems", n_results=3)
    print(f"✅ Found {len(results)} results for 'passive voice problems'")
    
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Score: {result.get('hybrid_score', 0):.3f}")
        print(f"Text: {result['text'][:100]}...")
    
    # Get stats
    stats = store.get_collection_stats()
    print(f"\n📊 Collection Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test retrieval system
    test_results = store.test_retrieval()
    print(f"\n🧪 Retrieval Test Results:")
    for query, result in test_results.items():
        print(f"  '{query}': {result.get('results_count', 0)} results")
