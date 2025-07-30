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
    logging.warning(f"RAG helper not available for {__name__}")

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Use 'tap' instead of 'click' or 'press' for touch interactions
    touch_click_patterns = [r'\bclick\b', r'\bpress\b']
    for pattern in touch_click_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            # Determine if context is about touch interactions
            context = content[max(0, match.start()-30):match.end()+30].lower()
            if 'touchscreen' in context or 'touch screen' in context or 'touch' in context:
#                line_number = get_line_number(content, match.start())
                suggestions.append("Use 'tap' instead of '{match.group()}' for touch interactions.")

    # Rule 2: Use 'double-tap' for tapping twice quickly
    double_tap_pattern = r'\bdouble\s+tap\b'
    matches = re.finditer(double_tap_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Correct usage; no action needed
        pass

    # Check for 'double-click' in touch context
    double_click_pattern = r'\bdouble\s+click\b'
    matches = re.finditer(double_click_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context = content[max(0, match.start()-30):match.end()+30].lower()
        if 'touch' in context:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'double-tap' instead of 'double-click' for touch interactions.")

    # Rule 3: Use 'press and hold' instead of 'long press'
    long_press_pattern = r'\blong\s+press\b'
    matches = re.finditer(long_press_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'press and hold' instead of 'long press'.")

    # Rule 4: Use 'swipe' to describe touch gestures that move content
    # Check for misuse of 'scroll' in touch context
    scroll_pattern = r'\bscroll\b'
    matches = re.finditer(scroll_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context = content[max(0, match.start()-30):match.end()+30].lower()
        if 'touch' in context or 'swipe' in context:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'swipe' instead of 'scroll' when referring to touch gestures.")

    # Rule 5: Use 'pinch' and 'stretch' for zooming in and out
    pinch_zoom_patterns = [r'\bpinch\b', r'\bstretch\b']
    for pattern in pinch_zoom_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            # Correct usage; no action needed
            pass

    # Rule 6: Use 'rotate' for rotating objects with touch
    # Correct usage; generally no action needed unless misused

    # Rule 7: Use 'slide' to describe moving an object on the screen
    # Check for misuse of 'drag' in touch context
    drag_pattern = r'\bdrag\b'
    matches = re.finditer(drag_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context = content[max(0, match.start()-30):match.end()+30].lower()
        if 'touch' in context:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'slide' instead of 'drag' when referring to touch interactions.")

    # Rule 8: Use 'flick' to scroll quickly
    flick_pattern = r'\bflick\b'
    matches = re.finditer(flick_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Correct usage; no action needed
        pass

    # Rule 9: Avoid platform-specific terminology unless necessary
    platform_terms = ['Force Touch', '3D Touch']
    for term in platform_terms:
        pattern = rf'\b{term}\b'
        matches = re.finditer(pattern, content)
        for match in matches:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Avoid platform-specific terms like '{match.group()}' unless necessary.")

    return suggestions if suggestions else []
