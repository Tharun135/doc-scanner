# enhanced_rag/__init__.py
"""
Enhanced RAG system for DocScanner with improved chunking, hybrid retrieval, and constrained prompting.

This package provides a comprehensive upgrade to the existing RAG system with:
- Advanced semantic chunking with rich metadata
- High-quality embeddings (OpenAI, Cohere, SentenceTransformers, Ollama)
- Hybrid retrieval (ChromaDB semantic + BM25 + cross-encoder re-ranking)
- Structured prompting with style guide conditioning
- Feedback loop and continuous adaptation
- Performance monitoring and caching
- Context-aware optimization

Quick Start:
    from enhanced_rag import get_advanced_rag_system, AdvancedRAGConfig
    
    # Configure the system
    config = AdvancedRAGConfig(
        embedding_provider="openai",  # or "sentence_transformers", "cohere", "ollama"
        enable_reranking=True,
        enable_feedback=True
    )
    
    # Initialize with your ChromaDB collection
    rag = get_advanced_rag_system(chroma_collection, config)
    
    # Get advanced suggestions
    response = rag.get_advanced_suggestion(
        feedback_text="passive voice detected",
        sentence_context="The file was created by the system.",
        rule_id="passive-voice"
    )
"""

# Advanced integration (main entry point)
try:
    from .advanced_integration import (
        AdvancedRAGSystem,
        AdvancedRAGConfig, 
        get_advanced_rag_system,
        create_advanced_rag_system
    )
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

# Advanced components
if ADVANCED_AVAILABLE:
    try:
        from .advanced_chunking import (
            AdvancedSemanticChunker,
            EnhancedChunk,
            chunk_document_advanced
        )
        
        from .advanced_embeddings import (
            AdvancedEmbeddingManager,
            get_embedding_manager
        )
        
        from .advanced_retrieval import (
            AdvancedHybridRetriever,
            AdvancedRetrievalResult,
            create_advanced_retriever
        )
        
        from .advanced_prompts import (
            AdvancedPromptManager,
            StyleGuideRule,
            PromptTemplate,
            get_prompt_manager
        )
        
        from .feedback_evaluation import (
            FeedbackEvaluationSystem,
            UserFeedback,
            RetrievalMetrics,
            GenerationMetrics,
            get_feedback_system
        )
    except ImportError:
        pass

# Legacy system (for backwards compatibility) - make optional
try:
    from .enhanced_rag_system import EnhancedRAGSystem, get_enhanced_rag_system
    from .enhanced_vectorstore import EnhancedVectorStore, get_enhanced_store
    from .hybrid_retrieval import HybridRetriever, RetrievalResult
    from .rag_prompt_templates import EnhancedRAGPrompts, RAGResponseFormatter, RAGContext
    from .chunking import (
        chunk_document_hierarchical,
    prepare_chunk_for_embedding,
    create_enhanced_metadata,
    chunk_by_paragraphs
)
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

__version__ = "2.0.0"
__author__ = "DocScanner Team"

# Main exports for easy integration
__all__ = []

if ADVANCED_AVAILABLE:
    __all__.extend([
        'AdvancedRAGSystem',
        'AdvancedRAGConfig', 
        'get_advanced_rag_system',
        'create_advanced_rag_system'
    ])

if LEGACY_AVAILABLE:
    __all__.extend([
        # Main system
        'EnhancedRAGSystem',
        'get_enhanced_rag_system',
        
        # Vector store
        'EnhancedVectorStore', 
        'get_enhanced_store',
        
        # Retrieval
        'HybridRetriever',
        'RetrievalResult',
        
        # Prompting
        'EnhancedRAGPrompts',
        'RAGResponseFormatter',
        'RAGContext',
        
        # Chunking
        'chunk_document_hierarchical',
        'prepare_chunk_for_embedding',
        'create_enhanced_metadata',
        'chunk_by_paragraphs'
    ])

# Package-level configuration
DEFAULT_CONFIG = {
    "collection_name": "docscanner_enhanced",
    "model_name": "phi3:mini",
    "hybrid_alpha": 0.6,
    "max_context_chunks": 3,
    "timeout_seconds": 2.0,
    "max_sentences_per_chunk": 5
}

def configure(config_dict: dict):
    """Update default configuration"""
    DEFAULT_CONFIG.update(config_dict)

def get_config():
    """Get current configuration"""
    return DEFAULT_CONFIG.copy()

# Quick setup function (only if legacy available)
if LEGACY_AVAILABLE:
    def quick_setup(migrate_from_existing: bool = True) -> 'EnhancedRAGSystem':
        """
        Quick setup with automatic migration from existing system.
        
        Args:
            migrate_from_existing: Whether to migrate data from existing collection
        
        Returns:
            Configured EnhancedRAGSystem ready to use
        """
        rag_system = get_enhanced_rag_system()
        
        if migrate_from_existing:
            try:
                success = rag_system.vector_store.migrate_from_existing_collection()
                if success:
                    print("✅ Successfully migrated existing data to enhanced system")
                else:
                    print("⚠️ Migration failed, using fresh enhanced system")
            except Exception as e:
                print(f"⚠️ Migration not possible: {e}")
        
        return rag_system

# Compatibility layer for existing code
if LEGACY_AVAILABLE:
    def get_legacy_compatible_system():
        """
        Get enhanced system with legacy-compatible interface.
        Drop-in replacement for existing RAG calls.
        """
        return get_enhanced_rag_system()

# Performance testing utility
def run_performance_test(rag_system = None, num_queries: int = 10):
    """Run basic performance test"""
    if rag_system is None:
        rag_system = get_enhanced_rag_system()
    
    test_queries = [
        ("passive voice detected", "The file was created by the system.", "passive-voice"),
        ("adverb usage", "You can easily complete this task really quickly.", "adverb-usage"),
        ("click on usage", "Click on the Save button to continue.", "click-on"),
        ("modal verb", "You should save the file before closing.", "modal-verbs"),
        ("all caps", "IMPORTANT: Save your work frequently.", "all-caps")
    ] * (num_queries // 5 + 1)
    
    results = []
    for i, (feedback, sentence, rule_id) in enumerate(test_queries[:num_queries]):
        import time
        start = time.time()
        
        response = rag_system.get_rag_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            rule_id=rule_id
        )
        
        duration = time.time() - start
        results.append({
            "query": i + 1,
            "duration": duration,
            "success": response is not None,
            "confidence": response.get("confidence", "none") if response else "none"
        })
    
    # Calculate metrics
    total_time = sum(r["duration"] for r in results)
    success_rate = sum(r["success"] for r in results) / len(results)
    avg_time = total_time / len(results)
    
    print(f"📊 Performance Test Results ({num_queries} queries):")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time: {avg_time:.3f}s per query")
    print(f"  Success rate: {success_rate:.1%}")
    print(f"  Queries/second: {len(results)/total_time:.1f}")
    
    return results

# Installation check utility
def check_dependencies():
    """Check if all required dependencies are available"""
    missing = []
    
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
        except OSError:
            missing.append("spacy model: python -m spacy download en_core_web_sm")
    except ImportError:
        missing.append("spacy: pip install spacy")
    
    try:
        import chromadb
    except ImportError:
        missing.append("chromadb: pip install chromadb")
    
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        missing.append("rank-bm25: pip install rank-bm25")
    
    try:
        import requests
    except ImportError:
        missing.append("requests: pip install requests")
    
    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        return False
    else:
        print("✅ All dependencies satisfied")
        return True

if __name__ == "__main__":
    print(f"Enhanced RAG System v{__version__}")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if deps_ok:
        print("\n🚀 Quick test of enhanced RAG system:")
        rag = get_enhanced_rag_system()
        
        test_response = rag.get_rag_suggestion(
            feedback_text="passive voice detected",
            sentence_context="The document was created by the user.",
            rule_id="passive-voice"
        )
        
        if test_response:
            print("✅ Enhanced RAG system working!")
            print(f"  Sample correction: {test_response.get('suggested_correction', 'N/A')}")
            print(f"  Confidence: {test_response.get('confidence', 'N/A')}")
        else:
            print("⚠️ Enhanced RAG system needs setup")
    else:
        print("\n⚠️ Install missing dependencies first")
