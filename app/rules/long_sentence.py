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
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    try:
        nlp_model = _get_nlp()
        doc = nlp_model(text_content)
    except Exception as e:
        return []  # Return empty if spaCy fails

    # Flag long sentences (>25 words) - exclude titles and markdown tables
    for sent in doc.sents:
        # Skip if this appears to be a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
            continue
            
        # Skip markdown table separator rows (| --- | --- | etc.)
        sent_text = sent.text.strip()
        if re.match(r'^\|\s*---.*\|\s*$', sent_text) or '| --- |' in sent_text:
            continue
            
        # Skip markdown table rows (containing multiple | characters)
        if sent_text.count('|') >= 3 and ('| --- |' in sent_text or re.match(r'^\|.*\|.*\|', sent_text)):
            continue
            
        if len(sent) > 25:
            suggestions.append(f"Consider breaking this long sentence into shorter ones: '{sent.text}'")
    
    return suggestions
