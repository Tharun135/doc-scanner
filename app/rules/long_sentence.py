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

    # Flag long sentences (>25 words) - exclude titles
    for sent in doc.sents:
        # Skip if this appears to be a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
            continue
            
        if len(sent) > 25:
            suggestions.append(f"Consider breaking this long sentence into shorter ones: '{sent.text}'")
    
    return suggestions
