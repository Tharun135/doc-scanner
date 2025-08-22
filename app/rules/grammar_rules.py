import re
import spacy
from bs4 import BeautifulSoup

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    print("⚠️ RAG rule helper not available - using standard grammar rules only")
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Lazy load spaCy model to avoid Flask startup conflicts
nlp = None

def _get_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️ spaCy model en_core_web_sm not found - grammar rules disabled")
            nlp = False
    return nlp if nlp is not False else None

def check(content):
    suggestions = []
    
    # Lazy load spaCy model
    nlp = _get_nlp()
    if nlp is None:
        return suggestions

    # Extract clean text (strip HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # ------------------------------
    # Regex-based checks
    # ------------------------------
    # Multiple consecutive spaces rule removed per user request

    # Double punctuation check removed per user request
    # if re.search(r"[.!?]{2,}", text_content):
    #     suggestions.append("Avoid repeating punctuation (e.g., '!!' or '??').")

    # ------------------------------
    # spaCy-based grammar checks
    # ------------------------------
    for sent in doc.sents:
        # Skip titles and headings for grammar checks
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
            continue
            
        # Example 1: Subject–verb agreement (singular/plural mismatch)
        for token in sent:
            if token.tag_ == "VBZ" and token.head.tag_ == "NNS":
                suggestions.append(f"Check subject–verb agreement: '{sent.text.strip()}'")

        # Example 2: Sentence starts with lowercase (skip markdown info blocks)
        if sent.text[0].islower():
            # Skip markdown info/note syntax like: info "NOTICE", warning "TEXT", etc.
            if not re.match(r'^\s*(info|warning|note|tip|caution)\s*"', sent.text.strip(), re.IGNORECASE):
                suggestions.append(f"Start sentences with a capital letter: '{sent.text.strip()}'")

    # ------------------------------
    # RAG-based contextual checks (if available)
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="grammar")
        suggestions.extend(rag_suggestions)

    return suggestions
