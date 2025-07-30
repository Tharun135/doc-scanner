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
    
    # Rule: Correct use of 'assure', 'ensure', 'insure'
#    misuse_patterns = {
#        r'\bassure\b': "Use 'assure' to mean 'to put someone's mind at ease'.",
#        r'\bensure\b': "Use 'ensure' to mean 'to make certain'.",
#        r'\binsure\b': "Use 'insure' only when referring to insurance."
#    }
#    for pattern, guidance in misuse_patterns.items():
#        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
#        for match in matches:
#            suggestions.append(f"{guidance}")

    # Rule: Use 'ask' instead of 'request' if 'request' is used as a verb
    request_pattern = r'\brequest\b'
    matches = re.finditer(request_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Instead of doc[match.start()], we create a char_span
        start_char = match.start()
        end_char = match.end()
        span = doc.char_span(start_char, end_char)

        # If spaCy can't map these offsets to token boundaries, skip
        if span is None:
            continue

        # Check if any token in this char_span is used as a VERB
        if any(token.pos_ == "VERB" for token in span):
            suggestions.append(f"Use 'ask' instead of '{match.group()}' as a verb.")
    
    # Additional grammar rules can be added here as needed
    return suggestions if suggestions else []