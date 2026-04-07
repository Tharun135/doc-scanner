import os
import sys
import logging
from pathlib import Path

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_ingestion import DocumentLoader
from app.chunking_strategies import TextChunker
from app.advanced_retrieval import AdvancedRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reindex_all():
    """Reindex all documents in the guidelines folder."""
    guidelines_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'guidelines'))
    
    logger.info(f"🚀 Re-indexing started for: {guidelines_path}")
    
    # 1. Load documents
    loader = DocumentLoader()
    documents = loader.load_documents_from_folder(guidelines_path)
    
    if not documents:
        logger.warning("No documents found in guidelines folder.")
        return
    
    # 2. Chunk documents
    chunker = TextChunker(default_chunk_size=500)
    all_chunks = []
    for doc in documents:
        # Force source_type to style_guide for everything in guidelines folder
        doc['source_type'] = 'style_guide'
        chunks = chunker.chunk_document(doc, method='adaptive')
        all_chunks.extend(chunks)
    
    logger.info(f"🧩 Created {len(all_chunks)} chunks from {len(documents)} documents.")
    
    # 3. Index in Retriever
    retriever = AdvancedRetriever()
    success = retriever.index_chunks(all_chunks)
    
    if success:
        logger.info("✅ Re-indexing completed successfully!")
    else:
        logger.error("❌ Re-indexing failed.")

if __name__ == "__main__":
    reindex_all()
