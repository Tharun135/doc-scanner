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
    # Rule: Use 'biography' instead of 'bio' in formal contexts
    bio_pattern = r'\bbio\b'
    matches = re.finditer(bio_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'biography' instead of '{match.group()}' in formal contexts.")

    # Rule: Avoid using 'beep'; use 'sound' or 'alert' instead
    beep_pattern = r'\bbeep\b'
    matches = re.finditer(beep_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Avoid using '{match.group()}'; use 'sound' or 'alert' instead.")

    return suggestions if suggestions else []