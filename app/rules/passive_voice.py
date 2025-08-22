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

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []
    
    # Strip HTML tags
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # Detect passive voice: look for "auxpass" dependencies
    # Pre-process content to remove admonition lines entirely
    lines = text_content.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip lines that are markdown admonitions
        if re.match(r'^\s*!!!\s+\w+(?:\s+"[^"]*")?\s*.*$', line, re.IGNORECASE):
            continue
        filtered_lines.append(line)
    
    # Re-process the filtered content with spaCy
    filtered_content = '\n'.join(filtered_lines)
    if not filtered_content.strip():
        return suggestions
        
    filtered_doc = nlp(filtered_content)
    
    for token in filtered_doc:
        sentence_text = token.sent.text.strip()
        
        # Skip if token is in a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sentence_text, content):
            continue
            
        if token.dep_ == "auxpass":
            # Avoid duplicate suggestions for the same sentence
            suggestion = f"Avoid passive voice in sentence: '{sentence_text}'"
            if suggestion not in suggestions:
                suggestions.append(suggestion)
    
    return suggestions
