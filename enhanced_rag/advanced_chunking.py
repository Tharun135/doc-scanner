# enhanced_rag/advanced_chunking.py
"""
Advanced semantic chunking strategy implementing the improvements suggested:
- Semantic chunking based on meaning, not just line breaks
- Better chunk size management (300-700 tokens with overlap)
- Preserve structural cues (headings, bullet points, tables)
- Rich metadata with section titles, file names, versions
"""

import re
import spacy
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Load spaCy model with enhanced pipeline
try:
    nlp = spacy.load("en_core_web_sm")
    # Add custom sentencizer for technical documents
    if 'sentencizer' not in nlp.pipe_names:
        nlp.add_pipe('sentencizer')
    SPACY_AVAILABLE = True
except OSError:
    logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None
    SPACY_AVAILABLE = False


@dataclass
class EnhancedChunk:
    """Enhanced chunk with rich metadata and semantic information"""
    text: str
    chunk_id: str
    source_doc_id: str
    product: str
    version: str
    section_title: str
    section_level: int  # H1=1, H2=2, etc.
    paragraph_index: int
    chunk_index: int
    sentence_range: str
    structural_type: str  # 'paragraph', 'list_item', 'table_cell', 'code_block'
    token_count: int
    char_count: int
    overlap_info: Dict[str, Any]
    created_at: str
    rule_tags: List[str]
    context_prefix: str  # For embedding enhancement


class AdvancedSemanticChunker:
    """
    Advanced chunking strategy that implements all suggested improvements:
    - Semantic coherence over simple splits
    - Optimal chunk size with overlap
    - Structural awareness
    - Rich metadata
    """
    
    def __init__(self, 
                 target_chunk_size: int = 500,  # 300-700 token range
                 min_chunk_size: int = 300,
                 max_chunk_size: int = 700,
                 overlap_size: int = 75,  # 50-100 token overlap
                 preserve_structure: bool = True):
        """
        Initialize advanced semantic chunker.
        
        Args:
            target_chunk_size: Target tokens per chunk
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk  
            overlap_size: Token overlap between chunks
            preserve_structure: Whether to preserve document structure
        """
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.preserve_structure = preserve_structure
        
    def chunk_document_advanced(self,
                               document_text: str,
                               source_doc_id: str,
                               product: str = "docscanner",
                               version: str = "1.0",
                               additional_metadata: Dict[str, Any] = None) -> List[EnhancedChunk]:
        """
        Advanced document chunking with semantic awareness.
        
        Args:
            document_text: Raw document text
            source_doc_id: Unique document identifier
            product: Product name for metadata
            version: Version for metadata
            additional_metadata: Extra metadata to include
            
        Returns:
            List of enhanced chunks with rich metadata
        """
        logger.info(f"🔄 Advanced chunking document: {source_doc_id}")
        
        # Step 1: Parse document structure
        structured_sections = self._parse_document_structure(document_text)
        
        # Step 2: Create semantic chunks within each section
        all_chunks = []
        chunk_index = 0
        
        for section in structured_sections:
            section_chunks = self._chunk_section_semantically(
                section=section,
                source_doc_id=source_doc_id,
                product=product,
                version=version,
                start_chunk_index=chunk_index,
                additional_metadata=additional_metadata or {}
            )
            
            all_chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
            
        # Step 3: Add overlap between chunks for continuity
        overlapped_chunks = self._add_semantic_overlap(all_chunks)
        
        logger.info(f"✅ Created {len(overlapped_chunks)} advanced chunks from {len(structured_sections)} sections")
        return overlapped_chunks
    
    def _parse_document_structure(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Parse document into structured sections based on headings, lists, tables.
        
        Args:
            document_text: Raw document text
            
        Returns:
            List of structured sections with metadata
        """
        sections = []
        current_section = {
            'title': 'Introduction',
            'level': 0,
            'content': '',
            'type': 'paragraph',
            'start_index': 0
        }
        
        lines = document_text.split('\n')
        paragraph_index = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect headings (markdown style)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                # Save previous section if it has content
                if current_section['content'].strip():
                    current_section['end_index'] = i
                    current_section['paragraph_index'] = paragraph_index
                    sections.append(current_section.copy())
                    paragraph_index += 1
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                current_section = {
                    'title': title,
                    'level': level,
                    'content': '',
                    'type': 'heading',
                    'start_index': i,
                    'paragraph_index': paragraph_index
                }
                continue
                
            # Detect lists
            list_match = re.match(r'^[-*+]\s+(.+)$|^\d+\.\s+(.+)$', line)
            if list_match:
                list_content = list_match.group(1) or list_match.group(2)
                # Group list items together
                if current_section.get('type') != 'list':
                    if current_section['content'].strip():
                        current_section['end_index'] = i
                        sections.append(current_section.copy())
                        paragraph_index += 1
                    
                    current_section = {
                        'title': current_section['title'] + ' (List)',
                        'level': current_section['level'],
                        'content': list_content + '\n',
                        'type': 'list',
                        'start_index': i,
                        'paragraph_index': paragraph_index
                    }
                else:
                    current_section['content'] += list_content + '\n'
                continue
            
            # Detect code blocks
            if line.startswith('```') or line.startswith('    '):
                if current_section.get('type') != 'code':
                    if current_section['content'].strip():
                        current_section['end_index'] = i
                        sections.append(current_section.copy())
                        paragraph_index += 1
                    
                    current_section = {
                        'title': current_section['title'] + ' (Code)',
                        'level': current_section['level'],
                        'content': line + '\n',
                        'type': 'code',
                        'start_index': i,
                        'paragraph_index': paragraph_index
                    }
                else:
                    current_section['content'] += line + '\n'
                continue
            
            # Regular content
            if line:
                # If we were in a special type, close it
                if current_section.get('type') in ['list', 'code']:
                    current_section['end_index'] = i
                    sections.append(current_section.copy())
                    paragraph_index += 1
                    
                    current_section = {
                        'title': current_section['title'].split(' (')[0],  # Remove type suffix
                        'level': current_section['level'],
                        'content': line + '\n',
                        'type': 'paragraph',
                        'start_index': i,
                        'paragraph_index': paragraph_index
                    }
                else:
                    current_section['content'] += line + '\n'
            elif current_section['content'].strip():
                # Empty line - potential paragraph break
                current_section['content'] += '\n'
        
        # Add final section
        if current_section['content'].strip():
            current_section['end_index'] = len(lines)
            current_section['paragraph_index'] = paragraph_index
            sections.append(current_section)
        
        return sections
    
    def _chunk_section_semantically(self,
                                   section: Dict[str, Any],
                                   source_doc_id: str,
                                   product: str,
                                   version: str,
                                   start_chunk_index: int,
                                   additional_metadata: Dict[str, Any]) -> List[EnhancedChunk]:
        """
        Create semantic chunks from a document section.
        
        Args:
            section: Parsed section with structure info
            source_doc_id: Document identifier
            product: Product name
            version: Version string
            start_chunk_index: Starting index for chunks
            additional_metadata: Additional metadata
            
        Returns:
            List of enhanced chunks for this section
        """
        content = section['content'].strip()
        if not content:
            return []
        
        # Calculate token count (approximate)
        token_count = len(content.split())
        
        chunks = []
        
        if token_count <= self.max_chunk_size:
            # Section fits in one chunk
            chunk = self._create_enhanced_chunk(
                text=content,
                source_doc_id=source_doc_id,
                product=product,
                version=version,
                section=section,
                chunk_index=start_chunk_index,
                additional_metadata=additional_metadata
            )
            chunks.append(chunk)
        else:
            # Split section semantically
            semantic_splits = self._split_semantically(content, section['type'])
            
            current_chunk_text = ""
            current_tokens = 0
            chunk_index = start_chunk_index
            
            for split in semantic_splits:
                split_tokens = len(split.split())
                
                # Check if adding this split exceeds max size
                if current_tokens + split_tokens > self.max_chunk_size and current_chunk_text:
                    # Create chunk from current content
                    if current_tokens >= self.min_chunk_size:
                        chunk = self._create_enhanced_chunk(
                            text=current_chunk_text.strip(),
                            source_doc_id=source_doc_id,
                            product=product,
                            version=version,
                            section=section,
                            chunk_index=chunk_index,
                            additional_metadata=additional_metadata
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    # Start new chunk
                    current_chunk_text = split
                    current_tokens = split_tokens
                else:
                    # Add to current chunk
                    current_chunk_text += " " + split if current_chunk_text else split
                    current_tokens += split_tokens
            
            # Add final chunk if it has content
            if current_chunk_text.strip() and current_tokens >= self.min_chunk_size:
                chunk = self._create_enhanced_chunk(
                    text=current_chunk_text.strip(),
                    source_doc_id=source_doc_id,
                    product=product,
                    version=version,
                    section=section,
                    chunk_index=chunk_index,
                    additional_metadata=additional_metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_semantically(self, content: str, section_type: str) -> List[str]:
        """
        Split content semantically based on sentence boundaries and meaning.
        
        Args:
            content: Text content to split
            section_type: Type of section (paragraph, list, code, etc.)
            
        Returns:
            List of semantic splits
        """
        if section_type == 'list':
            # Split by list items
            return [item.strip() for item in re.split(r'\n(?=[-*+]|\d+\.)', content) if item.strip()]
        
        if section_type == 'code':
            # Keep code blocks together, split by logical breaks
            return [content]  # For now, keep code as single chunk
        
        # For paragraphs, split by sentences but group related sentences
        if SPACY_AVAILABLE and nlp:
            doc = nlp(content)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback sentence splitting
            sentences = re.split(r'[.!?]+(?=\s+[A-Z])', content)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        # Group sentences semantically (simple heuristic: group by topic similarity)
        grouped_sentences = self._group_sentences_semantically(sentences)
        
        return grouped_sentences
    
    def _group_sentences_semantically(self, sentences: List[str]) -> List[str]:
        """
        Group sentences that are semantically related.
        
        Args:
            sentences: List of individual sentences
            
        Returns:
            List of grouped sentence chunks
        """
        if not sentences:
            return []
        
        groups = []
        current_group = [sentences[0]]
        
        for i in range(1, len(sentences)):
            current_sentence = sentences[i]
            prev_sentence = sentences[i-1]
            
            # Simple semantic grouping heuristics
            should_group = (
                # Same subject/topic (simple keyword overlap)
                len(set(current_sentence.lower().split()) & set(prev_sentence.lower().split())) >= 2
                # Short sentences should group together
                or len(current_sentence.split()) < 10
                # Pronouns suggest continuation
                or re.match(r'^(This|That|It|They|These|Those)', current_sentence)
                # Sequential indicators
                or re.match(r'^(First|Second|Third|Next|Then|Finally|However|Therefore)', current_sentence)
            )
            
            if should_group and len(' '.join(current_group + [current_sentence]).split()) <= self.target_chunk_size:
                current_group.append(current_sentence)
            else:
                # Start new group
                groups.append(' '.join(current_group))
                current_group = [current_sentence]
        
        # Add final group
        if current_group:
            groups.append(' '.join(current_group))
        
        return groups
    
    def _create_enhanced_chunk(self,
                              text: str,
                              source_doc_id: str,
                              product: str,
                              version: str,
                              section: Dict[str, Any],
                              chunk_index: int,
                              additional_metadata: Dict[str, Any]) -> EnhancedChunk:
        """
        Create an enhanced chunk with rich metadata.
        
        Args:
            text: Chunk text content
            source_doc_id: Document identifier
            product: Product name
            version: Version string
            section: Section metadata
            chunk_index: Index of this chunk
            additional_metadata: Additional metadata
            
        Returns:
            Enhanced chunk with full metadata
        """
        # Generate unique chunk ID
        chunk_content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        chunk_id = f"{source_doc_id}_{chunk_index}_{chunk_content_hash}"
        
        # Count tokens and chars
        token_count = len(text.split())
        char_count = len(text)
        
        # Generate sentence range info
        if SPACY_AVAILABLE and nlp:
            doc = nlp(text)
            sentence_count = len(list(doc.sents))
            sentence_range = f"1-{sentence_count}" if sentence_count > 1 else "1"
        else:
            sentence_count = len(re.split(r'[.!?]+', text))
            sentence_range = f"1-{sentence_count}" if sentence_count > 1 else "1"
        
        # Create context prefix for embedding enhancement
        context_prefix = f"[product:{product}] [version:{version}] [section:{section['title']}]"
        
        # Extract rule tags from content
        rule_tags = self._extract_rule_tags(text)
        
        return EnhancedChunk(
            text=text,
            chunk_id=chunk_id,
            source_doc_id=source_doc_id,
            product=product,
            version=version,
            section_title=section['title'],
            section_level=section['level'],
            paragraph_index=section['paragraph_index'],
            chunk_index=chunk_index,
            sentence_range=sentence_range,
            structural_type=section['type'],
            token_count=token_count,
            char_count=char_count,
            overlap_info={},  # Will be filled by overlap function
            created_at=datetime.now().isoformat(),
            rule_tags=rule_tags,
            context_prefix=context_prefix
        )
    
    def _extract_rule_tags(self, text: str) -> List[str]:
        """
        Extract relevant rule tags from text content.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of relevant rule tags
        """
        tags = []
        text_lower = text.lower()
        
        # Grammar and style tags
        if re.search(r'\b(passive|was|were|is|are)\s+\w+ed\b', text_lower):
            tags.append('passive_voice')
        
        if re.search(r'\b(very|really|quite|rather|extremely)\b', text_lower):
            tags.append('adverbs')
        
        if re.search(r'\b(click on|may|might|could|should)\b', text_lower):
            tags.append('modal_verbs')
        
        if len(text.split()) > 25:
            tags.append('long_sentences')
        
        if re.search(r'\b(configure|setup|install|create)\b', text_lower):
            tags.append('procedures')
        
        if re.search(r'\b(error|warning|note|important)\b', text_lower):
            tags.append('alerts')
        
        return tags
    
    def _add_semantic_overlap(self, chunks: List[EnhancedChunk]) -> List[EnhancedChunk]:
        """
        Add semantic overlap between consecutive chunks for continuity.
        
        Args:
            chunks: List of chunks to add overlap to
            
        Returns:
            List of chunks with overlap information added
        """
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Add overlap with previous chunk
            if i > 0:
                prev_chunk = chunks[i-1]
                overlap_text = self._create_overlap(prev_chunk.text, chunk.text, direction='previous')
                chunk.overlap_info['previous'] = {
                    'chunk_id': prev_chunk.chunk_id,
                    'overlap_text': overlap_text,
                    'token_count': len(overlap_text.split()) if overlap_text else 0
                }
            
            # Add overlap with next chunk
            if i < len(chunks) - 1:
                next_chunk = chunks[i+1]
                overlap_text = self._create_overlap(chunk.text, next_chunk.text, direction='next')
                chunk.overlap_info['next'] = {
                    'chunk_id': next_chunk.chunk_id,
                    'overlap_text': overlap_text,
                    'token_count': len(overlap_text.split()) if overlap_text else 0
                }
            
            overlapped_chunks.append(chunk)
        
        return overlapped_chunks
    
    def _create_overlap(self, text1: str, text2: str, direction: str) -> str:
        """
        Create semantic overlap between two text chunks.
        
        Args:
            text1: First text chunk
            text2: Second text chunk
            direction: 'previous' or 'next'
            
        Returns:
            Overlap text to include
        """
        if direction == 'previous':
            # Take last part of previous chunk
            words = text1.split()
            overlap_words = words[-self.overlap_size:] if len(words) > self.overlap_size else words
            return ' '.join(overlap_words)
        else:
            # Take first part of next chunk
            words = text2.split()
            overlap_words = words[:self.overlap_size] if len(words) > self.overlap_size else words
            return ' '.join(overlap_words)


def chunk_document_advanced(document_text: str,
                           source_doc_id: str,
                           product: str = "docscanner",
                           version: str = "1.0",
                           additional_metadata: Dict[str, Any] = None) -> List[EnhancedChunk]:
    """
    Convenience function for advanced document chunking.
    
    Args:
        document_text: Raw document text
        source_doc_id: Unique document identifier
        product: Product name for metadata
        version: Version for metadata
        additional_metadata: Extra metadata to include
        
    Returns:
        List of enhanced chunks with rich metadata
    """
    chunker = AdvancedSemanticChunker()
    return chunker.chunk_document_advanced(
        document_text=document_text,
        source_doc_id=source_doc_id,
        product=product,
        version=version,
        additional_metadata=additional_metadata
    )