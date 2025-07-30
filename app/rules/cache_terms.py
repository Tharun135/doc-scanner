import re
import spacy
from bs4 import BeautifulSoup
import html

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.warning(f"RAG helper not available for {__name__}")

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Ensure "disk cache" is used when referring to cache on a hard disk or SSD
    generic_cache_pattern = r'\b(cache)\b'
    disk_cache_terms = ['hard disk', 'SSD', 'disk', 'storage', 'disk drive']
    
    matches = re.finditer(generic_cache_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Check nearby words for disk-related context
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        
        # If any disk-related term is found, suggest using "disk cache"
        if any(term in context for term in disk_cache_terms):
            suggestions.append("Use 'disk cache' instead of 'cache' when referring to a disk-based cache (e.g., on a hard disk or SSD).")
    
    # Rule 2: Ensure "cache" is used correctly for memory-based cache
    disk_cache_pattern = r'\bdisk\s+cache\b'
    memory_cache_terms = ['memory', 'RAM', 'CPU cache', 'L1 cache', 'L2 cache', 'L3 cache']
    
    matches = re.finditer(disk_cache_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Check nearby words for memory-related context
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        
        # If memory-related terms are found, suggest using "cache" instead of "disk cache"
        if any(term in context for term in memory_cache_terms):
            suggestions.append("Use 'cache' instead of 'disk cache' when referring to memory-based caching (e.g., in RAM or CPU).")
    return suggestions if suggestions else []