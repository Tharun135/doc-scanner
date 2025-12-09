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

    # Rule 1: Use "call out" (two words) as a verb
    for token in doc:
        if token.text.lower() == "call" and token.head.text.lower() == "out" and token.dep_ == "ROOT" and token.head.dep_ == "prt":
            sentence = token.sent.text
            suggestions.append("Use 'call out' as two words when used as a verb (e.g., 'She will call out the names').")

    # Rule 2: Use "callout" (one word) as a noun or adjective
    callout_pattern = r'\b(callout)\b'
    matches = re.finditer(callout_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Ensure 'callout' is used as a noun or adjective (e.g., 'The callout was clear').")

    # Rule 3: Avoid "callout" when used as a verb
    callout_as_verb_pattern = r'\b(callout)\s+\w+ing\b'
    matches = re.finditer(callout_as_verb_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Avoid using 'callout' as a verb. Use 'call out' instead.")

    # Rule 4: Detect passive voice use of 'call out'
    for token in doc:
        if token.text.lower() == "called" and token.head.dep_ == "auxpass":
            sentence = token.sent.text
            suggestions.append("Consider rephrasing 'call out' in active voice.")

    return suggestions if suggestions else []
