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
    # Rule: Use 'back up' as a verb and 'backup' as a noun or adjective
    # Pattern to find 'backup' used as a verb
    backup_verb_pattern = r'\bbackup\b\s*(files|data|documents|your)\b'
    matches = re.finditer(backup_verb_pattern, content, flags=re.IGNORECASE)
    for match in matches:
    #    line_number = get_line_number(content, match.start())
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