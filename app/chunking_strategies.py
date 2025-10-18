"""
Advanced Chunking Strategies for DocScanner RAG System
Implements multiple chunking methods for optimal retrieval granularity.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# NLP imports
try:
    import spacy
    SPACY_AVAILABLE = True
    # Try to load the model
    try:
        nlp = spacy.load("en_core_web_sm")
        nlp.max_length = 3000000  # Increase max length to 2MB
    except OSError:
        nlp = None
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None

# Embedding imports for semantic chunking
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
    # Defer model loading until needed
    embedding_model = None
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    embedding_model = None

def get_embedding_model():
    """Get embedding model with lazy loading"""
    global embedding_model
    if EMBEDDINGS_AVAILABLE and embedding_model is None:
        try:
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
            embedding_model = None
    return embedding_model

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    id: str
    content: str
    start_char: int
    end_char: int
    chunk_type: str  # 'fixed', 'sentence', 'paragraph', 'semantic'
    token_count: int
    word_count: int
    source_doc_id: str
    metadata: Dict[str, Any]

class TextChunker:
    """Advanced text chunking with multiple strategies."""
    
    def __init__(self, default_chunk_size: int = 500, overlap_size: int = 50):
        self.default_chunk_size = default_chunk_size
        self.overlap_size = overlap_size
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        self.paragraph_separator = re.compile(r'\n\s*\n')
    
    def chunk_document(self, document: Dict[str, Any], method: str = "adaptive", 
                      chunk_size: int = None, **kwargs) -> List[Chunk]:
        """
        Chunk a document using the specified method.
        
        Args:
            document: Document dictionary from data_ingestion
            method: Chunking method ('fixed', 'sentence', 'paragraph', 'semantic', 'adaptive')
            chunk_size: Override default chunk size
            **kwargs: Additional parameters for specific methods
            
        Returns:
            List of Chunk objects
        """
        content = document.get('content', '')
        if not content.strip():
            return []
        
        chunk_size = chunk_size or self.default_chunk_size
        
        # Choose chunking method
        if method == "fixed":
            chunks = self._chunk_fixed_size(content, chunk_size, document['id'])
        elif method == "sentence":
            chunks = self._chunk_by_sentences(content, chunk_size, document['id'])
        elif method == "paragraph":
            chunks = self._chunk_by_paragraphs(content, chunk_size, document['id'])
        elif method == "semantic":
            chunks = self._chunk_semantic(content, chunk_size, document['id'], **kwargs)
        elif method == "adaptive":
            chunks = self._chunk_adaptive(content, document['id'], **kwargs)
        else:
            logger.warning(f"Unknown chunking method: {method}. Using fixed size.")
            chunks = self._chunk_fixed_size(content, chunk_size, document['id'])
        
        # Add document metadata to chunks
        for chunk in chunks:
            chunk.metadata.update({
                'source_file': document.get('file_name', ''),
                'source_type': document.get('source_type', ''),
                'doc_title': document.get('metadata', {}).get('title', ''),
                'created_at': document.get('created_at', ''),
                'chunking_method': method
            })
        
        logger.info(f"📝 Chunked document '{document.get('file_name', 'Unknown')}' "
                   f"into {len(chunks)} chunks using {method} method")
        
        return chunks
    
    def _chunk_fixed_size(self, content: str, chunk_size: int, doc_id: str) -> List[Chunk]:
        """Chunk text into fixed-size pieces with overlap."""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to end at word boundary if possible
            if end < len(content):
                # Look for the last space within reasonable distance
                last_space = content.rfind(' ', start, end)
                if last_space > start + chunk_size * 0.8:  # Only if we don't lose too much
                    end = last_space
            
            chunk_content = content[start:end].strip()
            
            if chunk_content:
                chunk = Chunk(
                    id=f"{doc_id}_chunk_{chunk_id:04d}",
                    content=chunk_content,
                    start_char=start,
                    end_char=end,
                    chunk_type="fixed",
                    token_count=len(chunk_content.split()),
                    word_count=len(chunk_content.split()),
                    source_doc_id=doc_id,
                    metadata={}
                )
                chunks.append(chunk)
                chunk_id += 1
            
            # Move start position with overlap
            start = max(end - self.overlap_size, start + 1)
            if start >= end:  # Prevent infinite loop
                break
        
        return chunks
    
    def _chunk_by_sentences(self, content: str, target_size: int, doc_id: str) -> List[Chunk]:
        """Chunk text by sentences, grouping to approximate target size."""
        if SPACY_AVAILABLE and nlp:
            # Use spaCy for better sentence segmentation
            doc = nlp(content)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback to regex-based sentence splitting
            sentences = [s.strip() for s in self.sentence_endings.split(content) if s.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        start_char = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed target size, finalize current chunk
            if current_chunk and (current_size + sentence_size > target_size):
                chunk_content = ' '.join(current_chunk)
                end_char = start_char + len(chunk_content)
                
                chunk = Chunk(
                    id=f"{doc_id}_sent_{chunk_id:04d}",
                    content=chunk_content,
                    start_char=start_char,
                    end_char=end_char,
                    chunk_type="sentence",
                    token_count=len(chunk_content.split()),
                    word_count=len(chunk_content.split()),
                    source_doc_id=doc_id,
                    metadata={'sentence_count': len(current_chunk)}
                )
                chunks.append(chunk)
                chunk_id += 1
                
                start_char = end_char
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Handle remaining sentences
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = Chunk(
                id=f"{doc_id}_sent_{chunk_id:04d}",
                content=chunk_content,
                start_char=start_char,
                end_char=start_char + len(chunk_content),
                chunk_type="sentence",
                token_count=len(chunk_content.split()),
                word_count=len(chunk_content.split()),
                source_doc_id=doc_id,
                metadata={'sentence_count': len(current_chunk)}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(self, content: str, target_size: int, doc_id: str) -> List[Chunk]:
        """Chunk text by paragraphs, splitting large paragraphs if needed."""
        paragraphs = self.paragraph_separator.split(content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        chunk_id = 0
        char_position = 0
        
        for paragraph in paragraphs:
            if len(paragraph) <= target_size:
                # Paragraph fits in one chunk
                chunk = Chunk(
                    id=f"{doc_id}_para_{chunk_id:04d}",
                    content=paragraph,
                    start_char=char_position,
                    end_char=char_position + len(paragraph),
                    chunk_type="paragraph",
                    token_count=len(paragraph.split()),
                    word_count=len(paragraph.split()),
                    source_doc_id=doc_id,
                    metadata={'is_complete_paragraph': True}
                )
                chunks.append(chunk)
                chunk_id += 1
            else:
                # Split large paragraph using sentence method
                para_chunks = self._chunk_by_sentences(paragraph, target_size, f"{doc_id}_para")
                for i, chunk in enumerate(para_chunks):
                    chunk.id = f"{doc_id}_para_{chunk_id:04d}_{i}"
                    chunk.chunk_type = "paragraph_split"
                    chunk.start_char += char_position
                    chunk.end_char += char_position
                    chunk.metadata['is_complete_paragraph'] = False
                    chunks.append(chunk)
                chunk_id += 1
            
            char_position += len(paragraph) + 2  # +2 for paragraph separator
        
        return chunks
    
    def _chunk_semantic(self, content: str, target_size: int, doc_id: str, 
                       similarity_threshold: float = 0.5) -> List[Chunk]:
        """Chunk text based on semantic similarity between sentences."""
        if not EMBEDDINGS_AVAILABLE:
            logger.warning("Sentence transformers not available. Using sentence chunking fallback.")
            return self._chunk_by_sentences(content, target_size, doc_id)
        
        # Get sentences
        if SPACY_AVAILABLE and nlp:
            doc = nlp(content)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            sentences = [s.strip() for s in self.sentence_endings.split(content) if s.strip()]
        
        if len(sentences) < 2:
            return self._chunk_fixed_size(content, target_size, doc_id)
        
        # Generate embeddings for sentences
        model = get_embedding_model()
        if model is None:
            logger.warning("Embedding model not available, falling back to fixed-size chunking")
            return self._chunk_fixed_size(content, target_size, doc_id)
            
        embeddings = model.encode(sentences)
        
        # Calculate similarity between consecutive sentences
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = np.dot(embeddings[i], embeddings[i + 1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
            )
            similarities.append(sim)
        
        # Find split points where similarity drops below threshold
        split_points = [0]
        current_chunk_size = 0
        
        for i, similarity in enumerate(similarities):
            sentence_size = len(sentences[i])
            
            # Split if similarity is low OR if chunk is getting too large
            if (similarity < similarity_threshold and current_chunk_size > target_size * 0.5) or \
               (current_chunk_size + sentence_size > target_size * 1.5):
                split_points.append(i + 1)
                current_chunk_size = 0
            else:
                current_chunk_size += sentence_size
        
        split_points.append(len(sentences))
        
        # Create chunks
        chunks = []
        start_char = 0
        
        for i in range(len(split_points) - 1):
            start_sent = split_points[i]
            end_sent = split_points[i + 1]
            
            chunk_sentences = sentences[start_sent:end_sent]
            chunk_content = ' '.join(chunk_sentences)
            end_char = start_char + len(chunk_content)
            
            chunk = Chunk(
                id=f"{doc_id}_sem_{i:04d}",
                content=chunk_content,
                start_char=start_char,
                end_char=end_char,
                chunk_type="semantic",
                token_count=len(chunk_content.split()),
                word_count=len(chunk_content.split()),
                source_doc_id=doc_id,
                metadata={
                    'sentence_count': len(chunk_sentences),
                    'avg_similarity': np.mean(similarities[start_sent:end_sent-1]) if end_sent > start_sent + 1 else 1.0
                }
            )
            chunks.append(chunk)
            start_char = end_char + 1
        
        return chunks
    
    def _chunk_adaptive(self, content: str, doc_id: str, 
                       min_chunk_size: int = 200, max_chunk_size: int = 800) -> List[Chunk]:
        """
        Adaptive chunking that chooses the best method based on content characteristics.
        """
        # Analyze content characteristics
        char_count = len(content)
        word_count = len(content.split())
        line_count = len(content.split('\n'))
        paragraph_count = len(self.paragraph_separator.split(content))
        
        # Decide on chunking strategy
        if paragraph_count > 3 and char_count / paragraph_count < max_chunk_size:
            # Content has clear paragraph structure
            method = "paragraph"
            target_size = max_chunk_size
        elif EMBEDDINGS_AVAILABLE and word_count > 100:
            # Use semantic chunking for substantial content
            method = "semantic"
            target_size = (min_chunk_size + max_chunk_size) // 2
        elif word_count > 50:
            # Use sentence-based chunking
            method = "sentence"
            target_size = (min_chunk_size + max_chunk_size) // 2
        else:
            # Short content, use fixed size
            method = "fixed"
            target_size = min_chunk_size
        
        logger.info(f"🔍 Adaptive chunking chose {method} method for document "
                   f"(chars: {char_count}, words: {word_count}, paragraphs: {paragraph_count})")
        
        # Apply the chosen method
        if method == "paragraph":
            return self._chunk_by_paragraphs(content, target_size, doc_id)
        elif method == "semantic":
            return self._chunk_semantic(content, target_size, doc_id)
        elif method == "sentence":
            return self._chunk_by_sentences(content, target_size, doc_id)
        else:
            return self._chunk_fixed_size(content, target_size, doc_id)

def chunk_documents(documents: List[Dict[str, Any]], method: str = "adaptive", 
                   chunk_size: int = 500, **kwargs) -> List[Chunk]:
    """
    Convenience function to chunk multiple documents.
    
    Args:
        documents: List of document dictionaries
        method: Chunking method to use
        chunk_size: Target chunk size
        **kwargs: Additional parameters
        
    Returns:
        List of all chunks from all documents
    """
    chunker = TextChunker(default_chunk_size=chunk_size)
    all_chunks = []
    
    for document in documents:
        doc_chunks = chunker.chunk_document(document, method, chunk_size, **kwargs)
        all_chunks.extend(doc_chunks)
    
    logger.info(f"📚 Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
    return all_chunks

def get_chunking_statistics(chunks: List[Chunk]) -> Dict[str, Any]:
    """Generate statistics about the chunking results."""
    if not chunks:
        return {}
    
    chunk_sizes = [chunk.word_count for chunk in chunks]
    chunk_types = [chunk.chunk_type for chunk in chunks]
    
    stats = {
        'total_chunks': len(chunks),
        'avg_chunk_size': np.mean(chunk_sizes),
        'min_chunk_size': min(chunk_sizes),
        'max_chunk_size': max(chunk_sizes),
        'chunk_size_std': np.std(chunk_sizes),
        'chunk_types': {chunk_type: chunk_types.count(chunk_type) for chunk_type in set(chunk_types)},
        'total_words': sum(chunk_sizes),
        'methods_available': {
            'spacy': SPACY_AVAILABLE,
            'embeddings': EMBEDDINGS_AVAILABLE
        }
    }
    
    return stats
