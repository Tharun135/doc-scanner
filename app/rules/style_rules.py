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

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Extract plain text (remove HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # ------------------------------
    # Regex-based style checks
    # ------------------------------
    # Check for passive voice using "by" + past participle
    if re.search(r"\bby\s+\w+ed\b", text_content, flags=re.IGNORECASE):
        suggestions.append("Consider avoiding passive voice where possible.")

    # Check for multiple exclamation marks
    if re.search(r"!{2,}", text_content):
        suggestions.append("Avoid using multiple exclamation marks.")

    # Check for all-caps words (likely shouting)
    if re.search(r"\b[A-Z]{5,}\b", text_content):
        suggestions.append("Avoid using ALL CAPS for emphasis. Use bold or italics instead.")

    # ------------------------------
    # spaCy-based style checks
    # ------------------------------
    for sent in doc.sents:
        # Example 1: Long, wordy sentences
        if len(sent.text.split()) > 25:
            suggestions.append(f"Consider simplifying this sentence: '{sent.text.strip()}'")

        # Example 2: Adverbs ending with -ly (may weaken writing)
        for token in sent:
            if token.text.endswith("ly") and token.pos_ == "ADV":
                suggestions.append(f"Check use of adverb: '{token.text}' in sentence '{sent.text.strip()}'")

        # Example 3: Detecting overuse of 'very'
        if "very" in sent.text.lower():
            suggestions.append(f"Try replacing or removing 'very': '{sent.text.strip()}'")

    # ------------------------------
    # RAG-based contextual style checks (if available)
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="style")
        suggestions.extend(rag_suggestions)

    return suggestions
