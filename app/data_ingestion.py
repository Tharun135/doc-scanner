"""
Data Ingestion Module for DocScanner RAG System
Handles loading and processing documents from various sources into the knowledge base.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

# Document processing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Handles loading documents from various sources and formats."""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.html', '.htm', '.py', '.js', '.json', '.yaml', '.yml']
        if PDF_AVAILABLE:
            self.supported_formats.extend(['.pdf'])
        if DOCX_AVAILABLE:
            self.supported_formats.extend(['.docx', '.doc'])
    
    def load_documents_from_folder(self, folder_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Load all supported documents from a folder.
        
        Args:
            folder_path: Path to the folder containing documents
            recursive: Whether to search subfolders recursively
            
        Returns:
            List of document dictionaries with metadata
        """
        documents = []
        folder = Path(folder_path)
        
        if not folder.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return documents
        
        # Get all files (recursive or not)
        if recursive:
            files = folder.rglob('*')
        else:
            files = folder.iterdir()
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    doc = self.load_single_document(str(file_path))
                    if doc:
                        documents.append(doc)
                        logger.info(f"✅ Loaded document: {file_path.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {file_path.name}: {e}")
        
        logger.info(f"📚 Loaded {len(documents)} documents from {folder_path}")
        return documents
    
    def load_single_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load a single document and extract its content."""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return None
        
        # Generate document ID from file path and modification time
        doc_id = self._generate_doc_id(path)
        
        # Extract content based on file type
        content = ""
        doc_type = path.suffix.lower()
        
        try:
            if doc_type == '.pdf' and PDF_AVAILABLE:
                content = self._extract_pdf_content(path)
            elif doc_type in ['.docx', '.doc'] and DOCX_AVAILABLE:
                content = self._extract_docx_content(path)
            elif doc_type in ['.html', '.htm']:
                content = self._extract_html_content(path)
            elif doc_type == '.md':
                content = self._extract_markdown_content(path)
            elif doc_type == '.txt':
                content = self._extract_text_content(path)
            elif doc_type in ['.py', '.js', '.json', '.yaml', '.yml']:
                content = self._extract_code_content(path)
            else:
                logger.warning(f"Unsupported file type: {doc_type}")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting content from {path.name}: {e}")
            return None
        
        if not content.strip():
            logger.warning(f"No content extracted from {path.name}")
            return None
        
        # Create document metadata
        document = {
            "id": doc_id,
            "source": "knowledge_base",
            "source_type": self._determine_source_type(path),
            "file_name": path.name,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "content": content.strip(),
            "word_count": len(content.split()),
            "char_count": len(content),
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "file_type": doc_type,
            "metadata": {
                "title": self._extract_title_from_content(content),
                "language": "en",  # Default, could be detected
                "tags": self._extract_tags_from_path(path)
            }
        }
        
        return document
    
    def _generate_doc_id(self, path: Path) -> str:
        """Generate a unique ID for a document based on path and modification time."""
        content = f"{path.absolute()}_{path.stat().st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _determine_source_type(self, path: Path) -> str:
        """Determine the type of document based on path and name."""
        name_lower = path.name.lower()
        parent_lower = path.parent.name.lower()
        
        if any(keyword in name_lower for keyword in ['style', 'guide', 'standard']):
            return 'style_guide'
        elif any(keyword in name_lower for keyword in ['manual', 'handbook', 'documentation']):
            return 'manual'
        elif any(keyword in name_lower for keyword in ['faq', 'question', 'help']):
            return 'faq'
        elif any(keyword in parent_lower for keyword in ['examples', 'templates']):
            return 'template'
        else:
            return 'document'
    
    def _extract_pdf_content(self, path: Path) -> str:
        """Extract text content from PDF files."""
        content = ""
        try:
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF content from {path}: {e}")
            # Return empty content if PDF extraction fails
            return ""
        return content.strip()
    
    def _extract_docx_content(self, path: Path) -> str:
        """Extract text content from DOCX files."""
        doc = DocxDocument(path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    
    def _extract_html_content(self, path: Path) -> str:
        """Extract text content from HTML files."""
        with open(path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)
    
    def _extract_markdown_content(self, path: Path) -> str:
        """Extract text content from Markdown files."""
        with open(path, 'r', encoding='utf-8') as file:
            md_content = file.read()
            # Convert to HTML first, then extract text
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
    
    def _extract_text_content(self, path: Path) -> str:
        """Extract content from plain text files."""
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_code_content(self, path: Path) -> str:
        """Extract content from code files (Python, JavaScript, JSON, YAML, etc.)."""
        try:
            # Ensure we have a Path object
            if isinstance(path, str):
                path = Path(path)
                
            # Try UTF-8 first, fallback to other encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                logger.warning(f"Could not decode file {path.name} with any supported encoding")
                return ""
            
            # Add some metadata to help with RAG retrieval
            file_info = f"# File: {path.name}\n# Type: {path.suffix}\n# Path: {path}\n\n"
            return file_info + content
            
        except Exception as e:
            logger.error(f"Error reading code file {path}: {e}")
            return ""
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract a title from the document content."""
        lines = content.strip().split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 100:  # Reasonable title length
                return line
        return "Untitled Document"
    
    def _extract_tags_from_path(self, path: Path) -> List[str]:
        """Extract relevant tags from file path and name."""
        tags = []
        
        # Add parent folder as tag
        if path.parent.name.lower() not in ['documents', 'files']:
            tags.append(path.parent.name.lower())
        
        # Extract tags from filename
        stem = path.stem.lower()
        if 'guide' in stem:
            tags.append('guide')
        if 'manual' in stem:
            tags.append('manual')
        if 'style' in stem:
            tags.append('style')
        if 'template' in stem:
            tags.append('template')
        
        return tags

def load_knowledge_base_from_config(config_path: str = "knowledge_base_config.json") -> List[Dict[str, Any]]:
    """
    Load knowledge base from a configuration file.
    
    Config format:
    {
        "folders": [
            {"path": "path/to/docs", "recursive": true, "type": "manual"},
            {"path": "path/to/styles", "recursive": false, "type": "style_guide"}
        ],
        "files": [
            {"path": "important_doc.pdf", "type": "faq"}
        ]
    }
    """
    documents = []
    loader = DocumentLoader()
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found: {config_path}")
        return documents
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load from folders
        for folder_config in config.get('folders', []):
            folder_docs = loader.load_documents_from_folder(
                folder_config['path'],
                folder_config.get('recursive', True)
            )
            # Override source type if specified
            if 'type' in folder_config:
                for doc in folder_docs:
                    doc['source_type'] = folder_config['type']
            documents.extend(folder_docs)
        
        # Load individual files
        for file_config in config.get('files', []):
            doc = loader.load_single_document(file_config['path'])
            if doc and 'type' in file_config:
                doc['source_type'] = file_config['type']
            if doc:
                documents.append(doc)
        
    except Exception as e:
        logger.error(f"Error loading from config: {e}")
    
    return documents

# Convenience functions
def quick_load_folder(folder_path: str) -> List[Dict[str, Any]]:
    """Quick function to load all documents from a folder."""
    loader = DocumentLoader()
    return loader.load_documents_from_folder(folder_path)

def get_supported_formats() -> List[str]:
    """Get list of supported file formats."""
    loader = DocumentLoader()
    return loader.supported_formats
