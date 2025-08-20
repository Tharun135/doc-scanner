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

nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # Flag long sentences (>25 words)
    for sent in doc.sents:
        if len(sent) > 25:
            suggestions.append(f"Consider breaking this long sentence into shorter ones: '{sent.text}'")
    
    return suggestions
