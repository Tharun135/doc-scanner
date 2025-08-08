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
    # Rule 1: Don't use 'calendar' as a verb, suggest 'schedule', 'list', or an alternative
    calendar_as_verb_pattern = r'\b(calendar(ed|ing)?)\b'
    matches = re.finditer(calendar_as_verb_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Avoid using 'calendar' as a verb. Consider using 'schedule' or 'list' instead of '{match.group()}'.")
    
    # Rule 2: Capitalize 'calendar' in product names (e.g., 'Google Calendar')
    product_name_pattern = r'\b(?:Google|Outlook)\s+calendar\b'
    matches = re.finditer(product_name_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        if 'Calendar' not in match.group():
            suggestions.append("Ensure 'Calendar' is capitalized when used in product names (e.g., 'Google Calendar').")

    # Rule 3: Avoid redundant phrases like 'calendar schedule' or 'calendar plan'
    redundant_calendar_pattern = r'\b(calendar)\s+(schedule|plan)\b'
    matches = re.finditer(redundant_calendar_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Avoid redundant phrases like 'calendar schedule' or 'calendar plan'. Consider using just '{match.group(1)}' or '{match.group(2)}'.")

    # Rule 4: Encourage specificity (e.g., 'event calendar', 'project calendar')
    generic_calendar_pattern = r'\bcalendar\b'
    matches = re.finditer(generic_calendar_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 30  # Check nearby words for specificity
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        if not any(specific_term in context.lower() for specific_term in ['event', 'project', 'release', 'work']):
            suggestions.append("Be specific when referring to a calendar (e.g., 'event calendar', 'project calendar').")
    
    # Rule 5: Avoid using 'calendar' in non-schedule contexts (e.g., lists or catalogs)
    non_schedule_context_pattern = r'\bcalendar\b'
    matches = re.finditer(non_schedule_context_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 30  # Check nearby words for improper usage
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        if any(term in context.lower() for term in ['items', 'list', 'catalog']):
            suggestions.append("Avoid using 'calendar' in non-schedule contexts. Consider using 'list' or 'catalog' instead.")
    return suggestions if suggestions else []