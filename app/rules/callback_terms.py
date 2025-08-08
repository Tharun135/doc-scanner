import re
from .spacy_utils import get_nlp_model
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
nlp = get_nlp_model()

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Use "call back" (two words) as a verb
    call_back_as_verb_pattern = r'\b(call\s+back)\b'
    matches = re.finditer(call_back_as_verb_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'call back' as two words when used as a verb (e.g., 'I will call you back').")
    
    # Rule 2: Use "callback" (one word) as a noun or adjective
    callback_as_noun_pattern = r'\b(callback)\b'
    matches = re.finditer(callback_as_noun_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Verify context, as "callback" should not be used as a verb
        context_window = 30
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        if 'called' in context.lower() or 'call' in context.lower():
            suggestions.append("Ensure 'callback' is used as a noun or adjective (e.g., 'The callback was scheduled').")
    
    # Rule 3: In developer content, avoid using "callback" to mean "callback function"
    callback_function_pattern = r'\bcallback\b'
    matches = re.finditer(callback_function_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 30
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        if 'function' not in context.lower():
            suggestions.append("In developer content, avoid using 'callback' to mean 'callback function'. Use 'callback function' instead.")
    
    # Rule 4: Avoid redundant mentions of "callback function" in developer content
    callback_function_redundant_pattern = r'\bcallback function\b'
    matches = re.finditer(callback_function_redundant_pattern, content, flags=re.IGNORECASE)
    occurrences = [match.start() for match in matches]
    if len(occurrences) > 1 and any(abs(occurrences[i] - occurrences[i-1]) < 100 for i in range(1, len(occurrences))):
        suggestions.append("Avoid redundant mentions of 'callback function' in close proximity.")
    return suggestions if suggestions else []