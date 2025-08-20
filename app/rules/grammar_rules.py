import re
import spacy
from bs4 import BeautifulSoup

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

# Load spaCy English model (make sure: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Extract clean text (strip HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # ------------------------------
    # Regex-based checks
    # ------------------------------
    # Example: Multiple spaces
    if re.search(r"\s{2,}", text_content):
        suggestions.append("Avoid using multiple consecutive spaces.")

    # Example: Double punctuation
    if re.search(r"[.!?]{2,}", text_content):
        suggestions.append("Avoid repeating punctuation (e.g., '!!' or '??').")

    # ------------------------------
    # spaCy-based grammar checks
    # ------------------------------
    for sent in doc.sents:
        # Example 1: Subject–verb agreement (singular/plural mismatch)
        for token in sent:
            if token.tag_ == "VBZ" and token.head.tag_ == "NNS":
                suggestions.append(f"Check subject–verb agreement: '{sent.text.strip()}'")

        # Example 2: Sentence starts with lowercase
        if sent.text[0].islower():
            suggestions.append(f"Start sentences with a capital letter: '{sent.text.strip()}'")

        # Example 3: Detect overly long sentences
        if len(sent.text.split()) > 30:
            suggestions.append(f"Consider breaking this long sentence: '{sent.text.strip()}'")

    # ------------------------------
    # RAG-based contextual checks (if available)
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="grammar")
        suggestions.extend(rag_suggestions)

    return suggestions
