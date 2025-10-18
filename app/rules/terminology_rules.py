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

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Load spaCy model lazily to avoid startup issues
nlp = None

def _get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
        nlp.max_length = 3000000  # Increase max length to 3MB
    return nlp

# Example terminology dictionary (customize for your manuals)
TERMINOLOGY = {
    "login": "log in (verb) / login (noun)",
    "setup": "set up (verb) / setup (noun)",
    "click on": "click",
    "shut down": "power off",
    "USB stick": "USB drive"
}

def check(content):
    suggestions = []

    # Extract plain text (strip HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    try:
        nlp_model = _get_nlp()
        doc = nlp_model(text_content)
    except Exception as e:
        # Fall back to basic processing if spaCy fails
        doc = None

    # ------------------------------
    # Regex-based terminology checks
    # ------------------------------
    for wrong, preferred in TERMINOLOGY.items():
        pattern = re.compile(rf"\b{wrong}\b", re.IGNORECASE)
        if pattern.search(text_content):
            suggestions.append(f"Use '{preferred}' instead of '{wrong}'.")

    # ------------------------------
    # spaCy-based terminology checks
    # ------------------------------
    if doc is not None:
        for token in doc:
            # Skip if token is in a title or heading
            if TITLE_UTILS_AVAILABLE and is_title_or_heading(token.sent.text.strip(), content):
                continue
                
            # Example: flagging ambiguous abbreviations
            if token.text.upper() in ["GUI", "API", "DB"]:
                suggestions.append(f"Spell out abbreviation '{token.text}' at first use.")

            # Example: consistency check for hyphenated terms
            if token.text.lower() in ["e-mail", "email"]:
                if "e-mail" in token.text.lower():
                    suggestions.append("Prefer 'email' instead of 'e-mail'.")

    # ------------------------------
    # RAG-based contextual terminology checks
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="terminology")
        suggestions.extend(rag_suggestions)

    return suggestions
