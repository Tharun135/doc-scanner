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
    # Rule 1: Use "cable" for physical connections; avoid using "cord" or "wire"
    cord_wire_pattern = r'\b(cord|wire)\b'
    matches = re.finditer(cord_wire_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'cable' instead of '{match.group()}' when referring to physical connections.")
    
    # Rule 2: Be specific with cable types (e.g., USB cable, Ethernet cable)
    generic_cable_pattern = r'\b(cable)\b'
    specific_cables = ['USB', 'Ethernet', 'HDMI', 'DisplayPort', 'Thunderbolt', 'VGA', 'DVI', 'power']
    
    matches = re.finditer(generic_cable_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Check nearby words for specific cable types
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        
        # If a specific cable type isn't mentioned, suggest being specific
        if not any(cable_type in context for cable_type in specific_cables):
            suggestions.append("Be specific about the cable type (e.g., 'USB cable', 'Ethernet cable').")
    
    return suggestions if suggestions else []