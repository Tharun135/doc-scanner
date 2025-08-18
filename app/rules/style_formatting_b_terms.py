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
    # Rule: Avoid using 'below' to refer to subsequent content
    # below_pattern = r'\bbelow\b'
    # matches = re.finditer(below_pattern, content, flags=re.IGNORECASE)
    # for match in matches:
    #     line_number = get_line_number(content, match.start())
    #     suggestions.append(f"Line {line_number}: Avoid using 'below' to refer to subsequent content; use specific references.")

    # Rule: Use 'bps' in lowercase for bits per second
    bps_pattern = r'\b[Bb]ps\b'
    matches = re.finditer(bps_pattern, content)
    for match in matches:
        if match.group() != 'bps':
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'bps' in lowercase for bits per second.")

    # Rule: Hyphenate 'bottom-left' and 'bottom-right' when used before a noun
    position_pattern = r'\b(bottom left|bottom right)\s+\w+'
    matches = re.finditer(position_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        term = match.group(1)
#        line_number = get_line_number(content, match.start())
        suggestions.append("Hyphenate '{term}' when used as an adjective before a noun (e.g., 'bottom-left corner').")

    return suggestions if suggestions else []