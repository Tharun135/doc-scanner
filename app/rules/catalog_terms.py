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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    """
    MSTP Rule: Use 'catalog' instead of 'catalogue'.
    Detects 'catalogue' and suggests using 'catalog' instead.
    """
    pattern = r'\bcatalogue\b'
    matches = re.finditer(pattern, content, flags=re.IGNORECASE)
    for match in matches:
        found_term = match.group()
        suggestions.append("Use 'catalog' instead of '{found_term}'."
        )
    return suggestions if suggestions else []