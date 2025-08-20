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
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []
    
    # Strip HTML tags
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # Detect passive voice: look for "auxpass" dependencies
    for token in doc:
        # Skip if token is in a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(token.sent.text.strip(), content):
            continue
            
        if token.dep_ == "auxpass":
            suggestions.append(f"Avoid passive voice in sentence: '{token.sent.text}'")
    
    return suggestions
