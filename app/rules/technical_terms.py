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
    # Rule: Capitalize 'Bluetooth'
    bluetooth_pattern = r'\bbluetooth\b'
    matches = re.finditer(bluetooth_pattern, content)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Capitalize 'Bluetooth' as it's a proper noun.")

    # Rule: Use 'bounding box' instead of 'bounding outline'
    bounding_outline_pattern = r'\bbounding outline\b'
    matches = re.finditer(bounding_outline_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'bounding box' instead of '{match.group()}'.")

    # Rule: Use 'Blu-ray Disc' with correct capitalization
    bluray_pattern = r'\bblu[-\s]?ray\s+disc\b'
    matches = re.finditer(bluray_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        if match.group() != 'Blu-ray Disc':
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'Blu-ray Disc' with 'Disc' capitalized.")

    return suggestions if suggestions else []