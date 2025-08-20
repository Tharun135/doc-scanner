import re
import spacy
from bs4 import BeautifulSoup
import html

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

nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # Common nominalization endings
    nominalization_pattern = re.compile(r".*(tion|ment|ness|ity|ance|ence|ship)$", re.IGNORECASE)

    for token in doc:
        # Skip if token is in a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(token.sent.text.strip(), content):
            continue
            
        if token.pos_ == "NOUN" and nominalization_pattern.match(token.text):
            suggestions.append(f"Consider replacing nominalization '{token.text}' with a verb form in sentence: '{token.sent.text}'")
    
    return suggestions
