# enhanced_rag/chunking.py
"""
Enhanced chunking strategy for RAG with hierarchical + context-prefix approach.
Implements semantic coherent chunks with rich metadata as specified in the requirements.
"""
import spacy
import hashlib
from typing import List, Dict, Any, Tuple
import re
from dataclasses import dataclass

# Load spaCy model (will be loaded once)
try:
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 3000000  # Increase max length to 2MB
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

@dataclass
class ChunkMetadata:
    """Structured metadata for each chunk"""
    source_doc_id: str
    product: str
    version: str
    section_title: str
    paragraph_index: int
    chunk_index: int
    sentence_range: str
    created_at: str
    rule_tags: List[str]
    char_count: int
    token_count: int


def sentences_from_text(text: str) -> List[str]:
    """Extract sentences from text using spaCy with fallback to simple splitting"""
    if nlp is None:
        # Fallback: simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def chunk_by_paragraphs(text: str, max_sentences: int = 5, min_sentences: int = 2) -> List[str]:
    """
    Chunk text by paragraphs with sentence grouping.
    Prefers paragraph/heading boundaries but sub-splits large paragraphs.
    
    Args:
        text: Input text to chunk
        max_sentences: Maximum sentences per chunk
        min_sentences: Minimum sentences per chunk (avoid tiny chunks)
    
    Returns:
        List of text chunks
    """
    # Split on double newlines into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    
    for para in paragraphs:
        sents = sentences_from_text(para)
        
        if not sents:
            continue
            
        # If paragraph has very few sentences, keep it as one chunk
        if len(sents) <= max_sentences:
            chunk = " ".join(sents)
            if len(chunk.split()) >= 20:  # At least 20 words
                chunks.append(chunk)
        else:
            # Split large paragraphs while maintaining sentence coherence
            for i in range(0, len(sents), max_sentences):
                chunk_sents = sents[i:i+max_sentences]
                if len(chunk_sents) >= min_sentences:  # Avoid tiny chunks
                    chunk = " ".join(chunk_sents)
                    chunks.append(chunk)
                elif i > 0:  # Merge small remainder with previous chunk
                    if chunks:
                        chunks[-1] += " " + " ".join(chunk_sents)
    
    return chunks


def prepare_chunk_for_embedding(chunk_text: str, metadata: Dict[str, Any]) -> str:
    """
    Enhance chunk with metadata prefix before embedding.
    This helps the embedding model capture product/section context.
    
    Args:
        chunk_text: Raw chunk text
        metadata: Metadata dict with product, version, section info
    
    Returns:
        Prefixed text ready for embedding
    """
    product = metadata.get('product', 'unknown')
    version = metadata.get('version', '')
    section = metadata.get('section_title', '')
    
    # Create contextual prefix
    prefix = f"[product:{product}] [version:{version}] [section:{section}] "
    
    return prefix + chunk_text


def create_enhanced_metadata(
    chunk_text: str,
    source_doc_id: str,
    product: str = "docscanner",
    version: str = "1.0",
    section_title: str = "",
    paragraph_index: int = 0,
    chunk_index: int = 0,
    sentence_range: str = "",
    rule_tags: List[str] = None
) -> Dict[str, Any]:
    """
    Create comprehensive metadata schema for chunks.
    
    Returns metadata dict suitable for ChromaDB storage.
    """
    import datetime
    
    if rule_tags is None:
        rule_tags = []
    
    # Auto-detect rule tags based on content
    text_lower = chunk_text.lower()
    auto_tags = []
    
    if any(word in text_lower for word in ["passive voice", "active voice"]):
        auto_tags.append("voice")
    if any(word in text_lower for word in ["adverb", "ly ending"]):
        auto_tags.append("adverbs")
    if any(word in text_lower for word in ["click on", "click the"]):
        auto_tags.append("click-patterns")
    if any(word in text_lower for word in ["should", "must", "avoid"]):
        auto_tags.append("rules")
    if "example" in text_lower or "for instance" in text_lower:
        auto_tags.append("examples")
    
    # Combine provided and auto-detected tags
    all_tags = list(set(rule_tags + auto_tags))
    
    # Count tokens (approximate)
    token_count = len(chunk_text.split())
    
    return {
        "source_doc_id": source_doc_id,
        "product": product,
        "version": version,
        "section_title": section_title,
        "paragraph_index": paragraph_index,
        "chunk_index": chunk_index,
        "sentence_range": sentence_range,
        "created_at": datetime.datetime.now().isoformat(),
        "rule_tags": ",".join(all_tags),  # Convert to string for ChromaDB
        "char_count": len(chunk_text),
        "token_count": token_count,
        "content_type": "writing_rule"
    }


def chunk_document_hierarchical(
    document_text: str,
    source_doc_id: str,
    product: str = "docscanner",
    version: str = "1.0",
    max_sentences_per_chunk: int = 5
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Perform hierarchical chunking of a document with rich metadata.
    
    Args:
        document_text: Full document text
        source_doc_id: Unique identifier for the source document
        product: Product name
        version: Product version
        max_sentences_per_chunk: Maximum sentences per chunk
    
    Returns:
        List of (chunk_text, metadata) tuples
    """
    chunks_with_metadata = []
    
    # Split into sections by headings if present
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    for line in document_text.split('\n'):
        if line.strip().startswith('#'):
            # Save previous section
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Start new section
            title = line.strip('#').strip() or "Untitled Section"
            current_section = {"title": title, "content": ""}
        else:
            current_section["content"] += line + '\n'
    
    # Don't forget the last section
    if current_section["content"].strip():
        sections.append(current_section)
    
    # Process each section
    chunk_global_index = 0
    
    for section_idx, section in enumerate(sections):
        section_title = section["title"]
        section_content = section["content"].strip()
        
        if not section_content:
            continue
            
        # Chunk this section
        section_chunks = chunk_by_paragraphs(
            section_content, 
            max_sentences=max_sentences_per_chunk
        )
        
        for para_idx, chunk_text in enumerate(section_chunks):
            # Estimate sentence range
            sentence_count = len(sentences_from_text(chunk_text))
            sentence_range = f"s{para_idx*max_sentences_per_chunk+1}-s{para_idx*max_sentences_per_chunk+sentence_count}"
            
            # Create metadata
            metadata = create_enhanced_metadata(
                chunk_text=chunk_text,
                source_doc_id=source_doc_id,
                product=product,
                version=version,
                section_title=section_title,
                paragraph_index=para_idx,
                chunk_index=chunk_global_index,
                sentence_range=sentence_range
            )
            
            chunks_with_metadata.append((chunk_text, metadata))
            chunk_global_index += 1
    
    return chunks_with_metadata


def generate_chunk_id(chunk_text: str, metadata: Dict[str, Any]) -> str:
    """Generate consistent, unique ID for a chunk"""
    # Create stable ID based on content and metadata
    id_source = f"{metadata['source_doc_id']}::{metadata['section_title']}::{metadata['chunk_index']}"
    content_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()[:8]
    return f"{id_source}::{content_hash}"


# Example usage and testing
if __name__ == "__main__":
    # Test the chunking system
    sample_text = """
# Writing Guidelines

## Passive Voice Issues

Passive voice can make text unclear and harder to read. Documents are written by authors, but active voice is preferred by readers.

Examples of passive voice:
- "The file was created by the system"
- "Errors were found in the code"

## Adverb Usage

Adverbs like "easily" and "simply" should be avoided. They often add unnecessary complexity.

Really good writing doesn't need many adverbs. Actually, most adverbs can be removed without losing meaning.

## Click Instructions

Don't say "click on the button." Instead, say "click the button" or "select the button."
This makes instructions more direct and clear.
    """
    
    print("Testing Enhanced Chunking System")
    print("=" * 50)
    
    chunks = chunk_document_hierarchical(
        document_text=sample_text,
        source_doc_id="test_doc_001",
        product="docscanner",
        version="2.0"
    )
    
    print(f"Generated {len(chunks)} chunks:")
    
    for i, (chunk_text, metadata) in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Section: {metadata['section_title']}")
        print(f"Rule Tags: {metadata['rule_tags']}")
        print(f"Text: {chunk_text[:100]}...")
        
        # Test embedding preparation
        enhanced_text = prepare_chunk_for_embedding(chunk_text, metadata)
        print(f"Enhanced: {enhanced_text[:100]}...")
