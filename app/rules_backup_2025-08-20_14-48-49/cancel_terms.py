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
    # Rule 1: Use "cancel" instead of "deselect" or "unmark"
    replace_terms = ["deselect", "unmark"]
    for token in doc:
        if token.text.lower() in replace_terms:
            suggestions.append("Use 'cancel' instead of '{token.text}' when referring to canceling a selection.")

    # Rule 2: Use "clear" for checkboxes, not "cancel"
    clear_for_checkboxes_pattern = r'\b(cancel)\s+(checkbox(es)?)\b'
    matches = re.finditer(clear_for_checkboxes_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'clear' for checkboxes, not 'cancel'.")

    # Rule 3: Ensure "canceled" and "canceling" are spelled with one "l"
    misspelled_canceled_pattern = r'\bcancel(l?)ed\b'
    misspelled_canceling_pattern = r'\bcancel(l?)ing\b'

    canceled_matches = re.finditer(misspelled_canceled_pattern, content, flags=re.IGNORECASE)
    for match in canceled_matches:
        if match.group(1):  # If extra "l" is found
            suggestions.append("Spell 'canceled' with one 'l'.")

    canceling_matches = re.finditer(misspelled_canceling_pattern, content, flags=re.IGNORECASE)
    for match in canceling_matches:
        if match.group(1):  # If extra "l" is found
            suggestions.append("Spell 'canceling' with one 'l'.")

    # Rule 4: Ensure "cancellation" is spelled with two "l"s
    cancellation_pattern = r'\bcancel(l?)ation\b'
    matches = re.finditer(cancellation_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        if not match.group(1):  # Missing second "l"
            suggestions.append("Spell 'cancellation' with two 'l's.")

    # Rule 5: Use "cancel" for ending processes before completion
    process_end_pattern = r'\b(cancel)\s+(the\s+process|request)\b'
    matches = re.finditer(process_end_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("'Cancel' is correctly used here to describe ending a process or request before it's complete.")

    # Rule: Suggest replacing "unmark" with "cancel"
    unmark_pattern = r'\bunmark\b'
    matches = re.finditer(unmark_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'cancel' instead of 'unmark'.")

    # Rule: Ensure "cancel" isn't used for checkboxes
    cancel_for_checkbox_pattern = r'\b(cancel)\s+(checkbox(es)?)\b'
    matches = re.finditer(cancel_for_checkbox_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'clear' for checkboxes, not 'cancel'.")

    # Rule: Ensure "cancel" is used to end processes
    incorrect_end_terms = ["stop", "abort"]
    for token in doc:
        if token.text.lower() in incorrect_end_terms and token.head.text.lower() == "process":
            suggestions.append("Use 'cancel' to describe ending the process, not '{token.text}'.")

    return suggestions if suggestions else []
