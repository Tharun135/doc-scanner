# fastapi_app/services/parser.py
"""
Document parsing and chunking service.
Supports: PDF, DOCX, HTML, TXT, Markdown, AsciiDoc, ZIP archives.
"""
import os
import re
import zipfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Document parsing libraries
import PyPDF2
from docx import Document as DocxDocument
from bs4 import BeautifulSoup
import nltk

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Unified document parser supporting multiple file formats.
    Extracts text and chunks it into manageable pieces.
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.html', '.htm', '.adoc', '.zip'}
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize parser with chunking parameters.
        
        Args:
            chunk_size: Target size of chunks in tokens (approximate)
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a document file and extract structured content.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary with:
                - text: Full extracted text
                - metadata: File metadata
                - pages: List of page texts (if applicable)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
        
        logger.info(f"Parsing file: {file_path.name} ({extension})")
        
        try:
            if extension == '.pdf':
                return self._parse_pdf(file_path)
            elif extension in {'.docx', '.doc'}:
                return self._parse_docx(file_path)
            elif extension in {'.html', '.htm'}:
                return self._parse_html(file_path)
            elif extension in {'.txt', '.md', '.adoc'}:
                return self._parse_text(file_path)
            elif extension == '.zip':
                return self._parse_zip(file_path)
            else:
                raise ValueError(f"Handler not implemented for {extension}")
                
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF file using PyPDF2."""
        pages = []
        text_parts = []
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                pages.append({
                    'page_number': page_num + 1,
                    'text': page_text
                })
                text_parts.append(page_text)
        
        full_text = '\n\n'.join(text_parts)
        
        return {
            'text': full_text,
            'pages': pages,
            'metadata': {
                'source': file_path.name,
                'type': 'pdf',
                'page_count': len(pages)
            }
        }
    
    def _parse_docx(self, file_path: Path) -> Dict[str, Any]:
        """Parse DOCX file using python-docx."""
        doc = DocxDocument(file_path)
        
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        full_text = '\n\n'.join(paragraphs)
        
        return {
            'text': full_text,
            'pages': [{'page_number': 1, 'text': full_text}],  # DOCX doesn't have pages
            'metadata': {
                'source': file_path.name,
                'type': 'docx',
                'paragraph_count': len(paragraphs)
            }
        }
    
    def _parse_html(self, file_path: Path) -> Dict[str, Any]:
        """Parse HTML file using BeautifulSoup."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'meta', 'link']):
            element.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return {
            'text': text,
            'pages': [{'page_number': 1, 'text': text}],
            'metadata': {
                'source': file_path.name,
                'type': 'html',
                'title': soup.title.string if soup.title else None
            }
        }
    
    def _parse_text(self, file_path: Path) -> Dict[str, Any]:
        """Parse plain text files (TXT, MD, AsciiDoc)."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        return {
            'text': text,
            'pages': [{'page_number': 1, 'text': text}],
            'metadata': {
                'source': file_path.name,
                'type': file_path.suffix.lstrip('.'),
                'size': len(text)
            }
        }
    
    def _parse_zip(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse ZIP archive by extracting and parsing each supported file.
        Returns combined content from all files.
        """
        extracted_texts = []
        all_pages = []
        
        with zipfile.ZipFile(file_path, 'r') as zf:
            for file_info in zf.namelist():
                file_ext = Path(file_info).suffix.lower()
                
                if file_ext in self.SUPPORTED_EXTENSIONS and file_ext != '.zip':
                    try:
                        # Extract to temp location
                        temp_path = f"/tmp/{Path(file_info).name}"
                        zf.extract(file_info, '/tmp')
                        
                        # Parse extracted file
                        parsed = self.parse_file(temp_path)
                        extracted_texts.append(f"=== {file_info} ===\n{parsed['text']}")
                        all_pages.extend(parsed['pages'])
                        
                        # Cleanup
                        os.remove(temp_path)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse {file_info} from ZIP: {e}")
        
        full_text = '\n\n'.join(extracted_texts)
        
        return {
            'text': full_text,
            'pages': all_pages,
            'metadata': {
                'source': file_path.name,
                'type': 'zip',
                'file_count': len(extracted_texts)
            }
        }
    
    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks based on sentences.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            # Approximate token count (1 token ≈ 0.75 words)
            sentence_tokens = len(sentence.split()) * 0.75
            
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_sentences = []
                overlap_tokens = 0
                
                # Add sentences from end for overlap
                for sent in reversed(current_chunk):
                    sent_tokens = len(sent.split()) * 0.75
                    if overlap_tokens + sent_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_tokens += sent_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences + [sentence]
                current_tokens = overlap_tokens + sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Format as chunk dictionaries
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'chunk_id': i,
                'text': chunk_text,
                'token_count': int(len(chunk_text.split()) * 0.75)
            }
            
            if metadata:
                chunk_dict['metadata'] = metadata.copy()
            
            chunk_dicts.append(chunk_dict)
        
        logger.info(f"Created {len(chunk_dicts)} chunks from {len(sentences)} sentences")
        return chunk_dicts
    
    def parse_and_chunk(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Complete pipeline: parse file and chunk the content.
        
        Args:
            file_path: Path to file to parse
            
        Returns:
            List of chunks with embeddings-ready structure
        """
        # Parse the document
        parsed = self.parse_file(file_path)
        
        # Chunk the text
        chunks = self.chunk_text(parsed['text'], parsed['metadata'])
        
        # Add unique IDs and source info
        source_name = parsed['metadata']['source']
        
        for i, chunk in enumerate(chunks):
            chunk['id'] = f"{source_name}_chunk_{i}"
            chunk['source'] = source_name
            
            # Add page info if available
            if parsed.get('pages'):
                # Try to determine which page this chunk is from (basic heuristic)
                chunk['page'] = (i * len(parsed['pages']) // len(chunks)) + 1
        
        return chunks
