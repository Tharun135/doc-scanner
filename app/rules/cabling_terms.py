import re
import spacy
from bs4 import BeautifulSoup
import html

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Use "cabling" instead of "wiring" when referring to a system of cables
    wiring_pattern = r'\bwiring\b'
    matches = re.finditer(wiring_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'cabling' instead of 'wiring' when referring to a system of cables.")
    
    # Rule 2: Be specific about the type of cabling (e.g., network cabling, fiber-optic cabling)
    generic_cabling_pattern = r'\bcabling\b'
    specific_cabling_types = ['network', 'fiber-optic', 'structured', 'coaxial', 'Ethernet', 'power']
    
    matches = re.finditer(generic_cabling_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Check nearby words for specific cabling types
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        
        # If a specific cabling type isn't mentioned, suggest being specific
        if not any(cabling_type in context for cabling_type in specific_cabling_types):
            suggestions.append("Be specific about the type of cabling (e.g., 'network cabling', 'fiber-optic cabling').")
    
    return suggestions if suggestions else []
