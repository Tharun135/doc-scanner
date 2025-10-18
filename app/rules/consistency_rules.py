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
        nlp.max_length = 3000000  # Increase max_length to handle large documents
    return nlp

def check(content):
    suggestions = []

    # Extract plain text (strip HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # ------------------------------
    # Step numbering consistency
    # ------------------------------
    step_pattern = re.compile(r"^\d+\.", re.MULTILINE)
    steps = step_pattern.findall(text_content)
    if steps:
        expected = [f"{i}." for i in range(1, len(steps) + 1)]
        if steps != expected:
            suggestions.append(
                "Inconsistent step numbering detected. Ensure sequential numbering (1., 2., 3., ...)."
            )

    # ------------------------------
    # Units of measure consistency
    # ------------------------------
    units = re.findall(r"\b\d+\s?(ms|sec|s|MB|Mb|KB|Gb|%)\b", text_content)
    if units:
        normalized = [u.lower() for u in units]
        if len(set(normalized)) > 1:
            suggestions.append(
                "Inconsistent units of measure found (e.g., sec vs s, MB vs Mb). Standardize units."
            )

    # ------------------------------
    # Terminology consistency
    # ------------------------------
    common_terms = {
        "login": "log in",
        "log-in": "log in",
        "Log in": "log in",
    }
    for wrong, correct in common_terms.items():
        if wrong in text_content and correct not in text_content:
            suggestions.append(
                f"Inconsistent terminology: found '{wrong}', but prefer '{correct}'."
            )

    # ------------------------------
    # Heading capitalization consistency
    # ------------------------------
    heading_pattern = re.compile(r"^#+\s+(.+)$", re.MULTILINE)
    for match in heading_pattern.findall(text_content):
        if match and not match[0].isupper():
            suggestions.append(
                f"Heading '{match}' may not follow capitalization rules. Ensure consistency."
            )

    # ------------------------------
    # Domain-specific consistency checks via RAG
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="consistency")
        suggestions.extend(rag_suggestions)

    return suggestions
