import re
import spacy
from bs4 import BeautifulSoup
import html

try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

try:
    nlp = spacy.load("en_core_web_sm")
    # Increase max_length to handle large documents (2MB limit)
    nlp.max_length = 3000000
    SPACY_AVAILABLE = True
except Exception as e:
    nlp = None
    SPACY_AVAILABLE = False
    print(f"Warning: spaCy model not available: {e}")

def check(content):
    if not SPACY_AVAILABLE or nlp is None:
        return []
        
    suggestions = []
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    # Handle very large texts by chunking them
    MAX_CHUNK_SIZE = 500000  # 500KB chunks to be safe
    
    if len(text_content) > MAX_CHUNK_SIZE:
        # Process in chunks
        chunks = [text_content[i:i+MAX_CHUNK_SIZE] for i in range(0, len(text_content), MAX_CHUNK_SIZE)]
        
        for chunk_index, chunk in enumerate(chunks):
            try:
                doc = nlp(chunk)
                # Process this chunk and adjust positions for the full document
                chunk_suggestions = _process_vague_terms_chunk(doc, chunk_index * MAX_CHUNK_SIZE)
                suggestions.extend(chunk_suggestions)
            except Exception as e:
                print(f"Warning: Error processing chunk {chunk_index} in vague_terms: {e}")
                continue
    else:
        # Process normally for smaller texts
        try:
            doc = nlp(text_content)
            suggestions.extend(_process_vague_terms_chunk(doc, 0))
        except Exception as e:
            print(f"Warning: Error processing text in vague_terms: {e}")
            return []
    
    return suggestions

def _process_vague_terms_chunk(doc, offset=0):
    """Process a spaCy doc for vague terms and return suggestions with position offset."""
    chunk_suggestions = []
    vague_terms = {"some", "several", "various", "stuff", "things"}
    
    for token in doc:
        # Skip if token is in a title or heading (for full content check)
        if TITLE_UTILS_AVAILABLE and offset == 0:
            # Only do title check for first chunk to avoid issues
            try:
                if is_title_or_heading(token.sent.text.strip(), ""):
                    continue
            except:
                pass  # Skip title check if it fails
            
        if token.text.lower() in vague_terms:
            # Create suggestion with adjusted position if needed
            suggestion = f"Avoid vague term '{token.text}' in sentence: '{token.sent.text}'"
            if offset > 0:
                suggestion += f" (at position ~{offset + token.idx})"
            chunk_suggestions.append(suggestion)
    
    return chunk_suggestions
