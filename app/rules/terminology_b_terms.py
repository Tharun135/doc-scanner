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
    # Rule: Use 'back up' as a verb and 'backup' as a noun or adjective
    # Pattern to find 'backup' used as a verb (only when preceded by verb indicators)
    backup_verb_pattern = r'\b(to|should|must|can|will|need to|please|remember to|don\'t forget to)\s+backup\b'
    matches = re.finditer(backup_verb_pattern, content, flags=re.IGNORECASE)
    for match in matches:
    #    line_number = get_line_number(content, match.start())
        suggestions.append("Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.")
    
    # Additional pattern for imperative verb usage: "backup your files" at start of sentence
    backup_imperative_pattern = r'(?:^|\.\s*)backup\s+(your|the|all)\s+.*?\b(files?|data|documents?)\b'
    matches = re.finditer(backup_imperative_pattern, content, flags=re.IGNORECASE | re.MULTILINE)
    for match in matches:
        suggestions.append("Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.")

    # Rule: Use 'blocklist' instead of 'blacklist'
    blacklist_pattern = r'\bblacklist\b'
    matches = re.finditer(blacklist_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'blocklist' instead of '{match.group()}'.")

    # Rule: Use 'restart' or 'start' instead of 'boot' in user-facing content
    boot_pattern = r'\bboot\b'
    matches = re.finditer(boot_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Check context to ensure it's not in a technical document
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'restart' or 'start' instead of '{match.group()}' in user-facing content.")

    # Rule: Capitalize 'Boolean' when referring to the data type
    boolean_pattern = r'\bboolean\b'
    matches = re.finditer(boolean_pattern, content)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Capitalize 'Boolean' when referring to the data type.")

    # Rule: Use 'bug' to refer to defects; 'fix' is acceptable as a noun in technical contexts
    # Check for 'fix' used in non-technical contexts
    fix_pattern = r'\bfix\b'
    matches = re.finditer(fix_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Determine if 'fix' is used appropriately
#        line_number = get_line_number(content, match.start())
        # If 'fix' is used as a noun in a non-technical context, suggest using 'correction' or 'update'
        suggestions.append("Ensure 'fix' is appropriate in this context; consider 'update' or 'correction'.")

    return suggestions if suggestions else []